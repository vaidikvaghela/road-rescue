from rest_framework import serializers
from .models import EmergencyRequest, Dispatch, Payment, ServiceRequest


class DispatchSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Dispatch
        fields = ['technician_name', 'technician_phone', 'vehicle_number', 'dispatched_at']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'razorpay_order_id', 'status', 'created_at']
        read_only_fields = ['id', 'razorpay_order_id', 'status', 'created_at']


class EmergencyRequestSerializer(serializers.ModelSerializer):
    dispatch        = DispatchSerializer(read_only=True)
    payment         = PaymentSerializer(read_only=True)
    status_display  = serializers.CharField(source='get_status_display',       read_only=True)
    issue_display   = serializers.CharField(source='get_issue_type_display',   read_only=True)
    vehicle_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)

    class Meta:
        model  = EmergencyRequest
        fields = [
            'id', 'requester_name', 'requester_phone',
            'vehicle_type', 'vehicle_display',
            'issue_type', 'issue_display',
            'notes', 'location_address', 'latitude', 'longitude',
            'status', 'status_display',
            'priority', 'assigned_provider', 'assigned_provider_id',
            'estimated_arrival', 'created_at', 'updated_at',
            'dispatch', 'payment',
        ]
        read_only_fields = [
            'id', 'priority', 'assigned_provider', 'assigned_provider_id',
            'estimated_arrival', 'created_at', 'updated_at',
        ]


class ServiceRequestSerializer(serializers.ModelSerializer):
    status_display  = serializers.CharField(source='get_status_display',       read_only=True)
    vehicle_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)
    customer_name   = serializers.SerializerMethodField()
    customer_email  = serializers.EmailField(source='customer.email',          read_only=True)
    customer_phone  = serializers.CharField(source='customer.phone',           read_only=True)
    provider_name   = serializers.CharField(source='provider.business_name',   read_only=True)
    provider_phone  = serializers.CharField(source='provider.phone',           read_only=True)
    payment         = PaymentSerializer(read_only=True)

    def get_customer_name(self, obj):
        return obj.customer.get_full_name() or obj.customer.username or obj.customer.email

    class Meta:
        model  = ServiceRequest
        fields = [
            'id', 'provider', 'provider_id', 'provider_name', 'provider_phone',
            'customer_name', 'customer_email', 'customer_phone',
            'service_type_text',
            'vehicle_type', 'vehicle_display',
            'vehicle_make', 'vehicle_model', 'vehicle_year', 'vehicle_reg_no',
            'notes', 'location_address',
            'status', 'status_display',
            'provider_note',
            'created_at', 'updated_at', 'accepted_at', 'completed_at',
            'payment',
        ]
        read_only_fields = [
            'id', 'provider_name', 'provider_phone',
            'customer_name', 'customer_email', 'customer_phone',
            'vehicle_display', 'status_display',
            'created_at', 'updated_at', 'accepted_at', 'completed_at',
            'payment',
        ]
