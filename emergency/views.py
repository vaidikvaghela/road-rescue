from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
import razorpay
from django.conf import settings
import json
from pywebpush import webpush, WebPushException
from django.contrib.auth import get_user_model
from .models import EmergencyRequest, Payment, ServiceRequest, PushSubscription
from .serializers import EmergencyRequestSerializer, ServiceRequestSerializer

User = get_user_model()

def send_push_to_user(user, title, body, url="/dashboard/"):
    if not user:
        return
    payload = json.dumps({"title": title, "body": body, "url": url})
    subs = PushSubscription.objects.filter(user=user)
    for sub in subs:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth}
                },
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.VAPID_ADMIN_EMAIL}
            )
        except Exception:
            pass



razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


class EmergencyRequestViewSet(viewsets.ModelViewSet):
    queryset          = EmergencyRequest.objects.all()
    serializer_class  = EmergencyRequestSerializer
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_permissions(self):
        if self.action in ('create', 'track'):
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        req = serializer.save()
        # Send Web Push notification to all providers
        payload = json.dumps({
            "title": "New Emergency Request!",
            "body": f"{req.requester_name} needs help with {req.get_issue_type_display()}.",
            "url": "/dashboard/"
        })
        subs = PushSubscription.objects.filter(user__role='provider')
        for sub in subs:
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {
                            "p256dh": sub.p256dh,
                            "auth": sub.auth
                        }
                    },
                    data=payload,
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": settings.VAPID_ADMIN_EMAIL}
                )
            except Exception:
                pass

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return EmergencyRequest.objects.none()

        if user.is_staff:
            return EmergencyRequest.objects.all()

        if user.role == 'provider':
            try:
                provider = user.provider_profile
            except Exception:
                return EmergencyRequest.objects.none()

            # Providers see:
            # 1. All pending (unassigned) requests — so they can browse & accept
            # 2. Requests already assigned to them
            from django.db.models import Q
            return EmergencyRequest.objects.filter(
                Q(status='pending', assigned_provider__isnull=True) |
                Q(assigned_provider=provider)
            ).order_by('-created_at')

        # Customer: their own requests only
        return EmergencyRequest.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)

    def perform_update(self, serializer):
        req  = self.get_object()
        user = self.request.user

        if user.is_staff:
            serializer.save()
            return

        if user.role == 'provider':
            try:
                provider = user.provider_profile
            except Exception:
                raise PermissionDenied("You do not have a provider profile.")

            # Provider can only update their own assigned jobs
            if req.assigned_provider is None or req.assigned_provider != provider:
                raise PermissionDenied("You can only update jobs assigned to you.")

            # Enforce allowed status progression
            new_status = serializer.validated_data.get('status', req.status)
            allowed = {
                'assigned':    ['en_route'],
                'en_route':    ['in_progress'],
                'in_progress': ['completed'],
            }
            if new_status != req.status and new_status not in allowed.get(req.status, []):
                raise PermissionDenied(
                    f"Cannot change status from '{req.status}' to '{new_status}'."
                )

            kwargs = {}
            if new_status == 'completed':
                kwargs['completed_at'] = timezone.now()
            serializer.save(**kwargs)
            
            # Notify customer of status change
            if new_status != req.status:
                send_push_to_user(
                    req.user,
                    "Request Update",
                    f"Your emergency request status is now: {new_status.replace('_', ' ').title()}",
                    url="/#track"
                )
            return

        raise PermissionDenied("You are not authorized to update this request.")

    # ── Custom Actions ────────────────────────────────────────────────────────

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def accept_job(self, request, pk=None):
        """Provider claims a pending request and becomes the assigned_provider."""
        user = request.user
        if user.role != 'provider':
            return Response({'error': 'Only providers can accept jobs.'}, status=403)

        try:
            provider = user.provider_profile
        except Exception:
            return Response({'error': 'Provider profile not found. Complete onboarding first.'}, status=400)

        try:
            req = EmergencyRequest.objects.get(pk=pk)
        except EmergencyRequest.DoesNotExist:
            return Response({'error': 'Request not found.'}, status=404)

        if req.status != 'pending' or req.assigned_provider is not None:
            return Response({'error': 'This request is no longer available.'}, status=409)

        req.assigned_provider = provider
        req.status            = 'assigned'
        req.assigned_at       = timezone.now()
        req.save(update_fields=['assigned_provider', 'status', 'assigned_at'])

        # Notify customer that provider accepted
        send_push_to_user(
            req.user,
            "Provider Assigned!",
            f"{provider.business_name} has accepted your emergency request.",
            url="/#track"
        )

        return Response(EmergencyRequestSerializer(req, context={'request': request}).data)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def track(self, request, pk=None):
        try:
            req = EmergencyRequest.objects.get(pk=pk)
            return Response(EmergencyRequestSerializer(req).data)
        except EmergencyRequest.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def create_payment(self, request, pk=None):
        try:
            req = EmergencyRequest.objects.get(pk=pk)
            amount = request.data.get('amount')
            if not amount:
                return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)

            amount_in_paise = int(float(amount) * 100)

            payment_data = {
                'amount': amount_in_paise,
                'currency': 'INR',
                'receipt': f'receipt_req_{req.pk}',
                'payment_capture': 1
            }
            try:
                order = razorpay_client.order.create(data=payment_data)
                order_id = order['id']
                order_amount = order['amount']
                order_currency = order['currency']
            except Exception as e:
                # Mock response for disconnected environments
                import uuid
                order_id = "order_mock_" + uuid.uuid4().hex[:14]
                order_amount = payment_data['amount']
                order_currency = payment_data['currency']

            payment, created = Payment.objects.get_or_create(
                request=req, defaults={'amount': amount}
            )
            if not created:
                payment.amount = amount
            payment.razorpay_order_id = order_id
            payment.status = 'pending'
            payment.save()

            return Response({
                'order_id': order_id,
                'amount':   order_amount,
                'currency': order_currency,
                'key_id':   settings.RAZORPAY_KEY_ID
            })

        except EmergencyRequest.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def verify_payment(self, request, pk=None):
        try:
            req     = EmergencyRequest.objects.get(pk=pk)
            payment = req.payment

            params_dict = {
                'razorpay_order_id':   request.data.get('razorpay_order_id'),
                'razorpay_payment_id': request.data.get('razorpay_payment_id'),
                'razorpay_signature':  request.data.get('razorpay_signature'),
            }

            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
                payment.razorpay_payment_id = params_dict['razorpay_payment_id']
                payment.razorpay_signature  = params_dict['razorpay_signature']
                payment.status = 'completed'
                payment.save()
                return Response({'status': 'Payment successful'})
            except razorpay.errors.SignatureVerificationError:
                payment.status = 'failed'
                payment.save()
                return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        except (EmergencyRequest.DoesNotExist, Payment.DoesNotExist):
            return Response({'error': 'Not found.'}, status=404)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def confirm_payment(self, request, pk=None):
        try:
            req = EmergencyRequest.objects.get(pk=pk)
            if req.assigned_provider and req.assigned_provider.user == request.user:
                if req.status != 'completed':
                    return Response({'error': 'Job must be completed first.'}, status=400)
                payment, _ = Payment.objects.get_or_create(request=req, defaults={'amount': 0})
                payment.status = 'completed'
                payment.save()
                return Response({'status': 'Payment confirmed manually.'})
            return Response({'error': 'Unauthorized'}, status=403)
        except EmergencyRequest.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def get_qr(self, request, pk=None):
        user = request.user
        if user.role != 'provider':
            return Response({'error': 'Only providers can generate QR codes.'}, status=403)
            
        try:
            req = EmergencyRequest.objects.get(pk=pk)
        except EmergencyRequest.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)
            
        amount = request.data.get('amount')
        if not amount:
            return Response({'error': 'Amount is required'}, status=400)
            
        amount_in_paise = int(float(amount) * 100)
        link_data = {
            "amount": amount_in_paise,
            "currency": "INR",
            "description": f"Payment for Emergency Request #{req.pk}",
            "customer": {
                "name": req.requester_name,
                "contact": req.requester_phone,
            }
        }
        try:
            payment_link = razorpay_client.payment_link.create(link_data)
            return Response({'short_url': payment_link['short_url']})
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ── Non-Emergency Service Request ──────────────────────────────────────────────

class ServiceRequestViewSet(viewsets.ModelViewSet):
    """
    Customer creates a ServiceRequest directed at a specific provider.
    Provider can then accept or decline it, and progress it to in_progress / completed.
    """
    serializer_class  = ServiceRequestSerializer
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ServiceRequest.objects.select_related('customer', 'provider').all()

        if user.role == 'provider':
            try:
                provider = user.provider_profile
                return ServiceRequest.objects.select_related('customer', 'provider').filter(provider=provider)
            except Exception:
                return ServiceRequest.objects.none()

        # Customer: only their own requests
        return ServiceRequest.objects.select_related('customer', 'provider').filter(customer=user)

    def perform_create(self, serializer):
        """Customer submits a service request to a specific provider."""
        if self.request.user.role not in ('customer', 'admin') and not self.request.user.is_staff:
            raise PermissionDenied("Only customers can create service requests.")
        req = serializer.save(customer=self.request.user, status='pending')
        
        # Send Web Push notification to the targeted provider
        payload = json.dumps({
            "title": "New Service Request!",
            "body": f"{req.customer.get_full_name() or req.customer.username} has requested a {req.service_type_text}.",
            "url": "/dashboard/"
        })
        subs = PushSubscription.objects.filter(user=req.provider.user)
        for sub in subs:
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {
                            "p256dh": sub.p256dh,
                            "auth": sub.auth
                        }
                    },
                    data=payload,
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": settings.VAPID_ADMIN_EMAIL}
                )
            except Exception:
                pass

    # ── Provider Actions ──────────────────────────────────────────────────────

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def accept(self, request, pk=None):
        """Provider accepts an incoming service request."""
        sr = self._get_sr_for_provider(pk, request.user)
        if isinstance(sr, Response):
            return sr
        if sr.status != 'pending':
            return Response({'error': 'Only pending requests can be accepted.'}, status=409)
        note = request.data.get('provider_note', '')
        sr.status      = 'accepted'
        sr.accepted_at = timezone.now()
        sr.provider_note = note
        sr.save(update_fields=['status', 'accepted_at', 'provider_note'])
        
        send_push_to_user(
            sr.customer,
            "Service Accepted",
            f"{sr.provider.business_name} has accepted your service request.",
            url="/#track"
        )
        return Response(ServiceRequestSerializer(sr).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def decline(self, request, pk=None):
        """Provider declines an incoming service request."""
        sr = self._get_sr_for_provider(pk, request.user)
        if isinstance(sr, Response):
            return sr
        if sr.status != 'pending':
            return Response({'error': 'Only pending requests can be declined.'}, status=409)
        note = request.data.get('provider_note', '')
        sr.status        = 'declined'
        sr.provider_note = note
        sr.save(update_fields=['status', 'provider_note'])
        
        send_push_to_user(
            sr.customer,
            "Service Declined",
            f"{sr.provider.business_name} declined your request. Note: {note}",
            url="/#track"
        )
        return Response(ServiceRequestSerializer(sr).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def start(self, request, pk=None):
        """Provider marks the job as in_progress."""
        sr = self._get_sr_for_provider(pk, request.user)
        if isinstance(sr, Response):
            return sr
        if sr.status != 'accepted':
            return Response({'error': 'Request must be accepted before starting.'}, status=409)
        sr.status = 'in_progress'
        sr.save(update_fields=['status'])
        
        send_push_to_user(
            sr.customer,
            "Service In Progress",
            f"{sr.provider.business_name} has started working on your request.",
            url="/#track"
        )
        return Response(ServiceRequestSerializer(sr).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        """Provider marks the job as completed."""
        sr = self._get_sr_for_provider(pk, request.user)
        if isinstance(sr, Response):
            return sr
        if sr.status != 'in_progress':
            return Response({'error': 'Request must be in_progress to complete.'}, status=409)
        sr.status       = 'completed'
        sr.completed_at = timezone.now()
        sr.save(update_fields=['status', 'completed_at'])
        # Increment provider total_jobs
        try:
            sr.provider.total_jobs += 1
            sr.provider.save(update_fields=['total_jobs'])
        except Exception:
            pass
            
        send_push_to_user(
            sr.customer,
            "Service Completed",
            f"{sr.provider.business_name} has completed your service request. Please proceed to payment.",
            url="/#track"
        )
        return Response(ServiceRequestSerializer(sr).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        """Customer cancels their own pending/accepted service request."""
        user = request.user
        try:
            sr = ServiceRequest.objects.get(pk=pk)
        except ServiceRequest.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)
        if sr.customer != user:
            return Response({'error': 'You can only cancel your own requests.'}, status=403)
        if sr.status in ('completed', 'cancelled'):
            return Response({'error': 'Cannot cancel a completed or already-cancelled request.'}, status=409)
        sr.status = 'cancelled'
        sr.save(update_fields=['status'])
        return Response(ServiceRequestSerializer(sr).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def get_qr(self, request, pk=None):
        sr = self._get_sr_for_provider(pk, request.user)
        if isinstance(sr, Response):
            return sr
            
        amount = request.data.get('amount')
        if not amount:
            return Response({'error': 'Amount is required'}, status=400)
            
        amount_in_paise = int(float(amount) * 100)
        link_data = {
            "amount": amount_in_paise,
            "currency": "INR",
            "description": f"Payment for Service Request #{sr.pk}",
            "customer": {
                "name": sr.customer.get_full_name() or sr.customer.username,
                "email": sr.customer.email,
            }
        }
        try:
            payment_link = razorpay_client.payment_link.create(link_data)
            
            # Save/update Payment record in DB
            payment, created = Payment.objects.get_or_create(
                service_request=sr,
                defaults={'amount': amount}
            )
            if not created:
                payment.amount = amount
            payment.status = 'pending'
            payment.save()
            
            return Response({'short_url': payment_link['short_url']})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def create_payment(self, request, pk=None):
        try:
            sr = ServiceRequest.objects.get(pk=pk)
            if sr.customer != request.user:
                return Response({'error': 'Unauthorized'}, status=403)
                
            amount = request.data.get('amount')
            if not amount:
                return Response({'error': 'Amount is required'}, status=400)

            amount_in_paise = int(float(amount) * 100)
            payment_data = {
                'amount': amount_in_paise,
                'currency': 'INR',
                'receipt': f'receipt_sr_{sr.pk}',
                'payment_capture': 1
            }
            try:
                order = razorpay_client.order.create(data=payment_data)
                order_id = order['id']
                order_amount = order['amount']
                order_currency = order['currency']
            except Exception as e:
                import uuid
                order_id = "order_mock_" + uuid.uuid4().hex[:14]
                order_amount = payment_data['amount']
                order_currency = payment_data['currency']

            payment, created = Payment.objects.get_or_create(
                service_request=sr, defaults={'amount': amount}
            )
            if not created:
                payment.amount = amount
            payment.razorpay_order_id = order_id
            payment.status = 'pending'
            payment.save()

            return Response({
                'order_id': order_id,
                'amount':   order_amount,
                'currency': order_currency,
                'key_id':   settings.RAZORPAY_KEY_ID
            })
        except ServiceRequest.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def verify_payment(self, request, pk=None):
        try:
            sr = ServiceRequest.objects.get(pk=pk)
            if sr.customer != request.user:
                return Response({'error': 'Unauthorized'}, status=403)
                
            payment = sr.payment
            params_dict = {
                'razorpay_order_id':   request.data.get('razorpay_order_id'),
                'razorpay_payment_id': request.data.get('razorpay_payment_id'),
                'razorpay_signature':  request.data.get('razorpay_signature'),
            }
            try:
                import razorpay
                razorpay_client.utility.verify_payment_signature(params_dict)
                payment.razorpay_payment_id = params_dict['razorpay_payment_id']
                payment.razorpay_signature  = params_dict['razorpay_signature']
                payment.status = 'completed'
                payment.save()
                return Response({'status': 'Payment successful'})
            except Exception:
                payment.status = 'failed'
                payment.save()
                return Response({'error': 'Invalid signature'}, status=400)
        except (ServiceRequest.DoesNotExist, Payment.DoesNotExist):
            return Response({'error': 'Not found.'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def confirm_payment(self, request, pk=None):
        resp_or_sr = self._get_sr_for_provider(pk, request.user)
        if isinstance(resp_or_sr, Response):
            return resp_or_sr
        sr = resp_or_sr
        if sr.status != 'completed':
            return Response({'error': 'Job must be completed first.'}, status=400)
        payment, _ = Payment.objects.get_or_create(service_request=sr, defaults={'amount': 0})
        payment.status = 'completed'
        payment.save()
        return Response({'status': 'Payment confirmed manually.'})

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_sr_for_provider(self, pk, user):
        if user.role != 'provider':
            return Response({'error': 'Only providers can perform this action.'}, status=403)
        try:
            provider = user.provider_profile
        except Exception:
            return Response({'error': 'Provider profile not found.'}, status=400)
        try:
            sr = ServiceRequest.objects.get(pk=pk)
        except ServiceRequest.DoesNotExist:
            return Response({'error': 'Service request not found.'}, status=404)
        if sr.provider != provider:
            return Response({'error': 'This request is not assigned to you.'}, status=403)
        return sr


class PushSubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        sub_info = request.data.get('subscription')
        if not sub_info:
            return Response({'error': 'Subscription data missing'}, status=400)
            
        endpoint = sub_info.get('endpoint')
        keys = sub_info.get('keys', {})
        p256dh = keys.get('p256dh', '')
        auth = keys.get('auth', '')
        
        sub, created = PushSubscription.objects.update_or_create(
            user=request.user,
            endpoint=endpoint,
            defaults={'p256dh': p256dh, 'auth': auth}
        )
        return Response({'success': True})

