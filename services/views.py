from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from django.db.models import Q
import math

from .models import ServiceType, ServiceProvider, Review
from .serializers import ServiceTypeSerializer, ServiceProviderSerializer, ServiceProviderListSerializer, ReviewSerializer


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    p1, p2 = math.radians(float(lat1)), math.radians(float(lat2))
    dp = math.radians(float(lat2) - float(lat1))
    dl = math.radians(float(lon2) - float(lon1))
    a  = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


class ServiceTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = ServiceType.objects.filter(is_active=True)
    serializer_class = ServiceTypeSerializer


class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset           = ServiceProvider.objects.filter(status='active')
    serializer_class   = ServiceProviderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields   = ['city', 'is_available', 'is_24_7']

    def get_serializer_class(self):
        if self.action == 'list':
            return ServiceProviderListSerializer
        return ServiceProviderSerializer

    def get_queryset(self):
        qs    = super().get_queryset()
        query = self.request.query_params.get('q')
        if query:
            qs = qs.filter(Q(business_name__icontains=query) | Q(city__icontains=query)).distinct()
        return qs

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        lat    = request.query_params.get('lat')
        lon    = request.query_params.get('lon')
        radius = float(request.query_params.get('radius', 20))
        if not lat or not lon:
            return Response({'error': 'lat and lon are required.'}, status=400)
        results = []
        for p in self.get_queryset().filter(latitude__isnull=False):
            d = haversine(lat, lon, p.latitude, p.longitude)
            if d <= radius:
                p.distance = round(d, 2)
                results.append(p)
        results.sort(key=lambda x: x.distance)
        return Response(ServiceProviderListSerializer(results, many=True, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def review(self, request, pk=None):
        provider = self.get_object()
        # Check if user already reviewed
        existing = Review.objects.filter(provider=provider, user=request.user).first()
        if existing:
            # Update existing review
            serializer = ReviewSerializer(existing, data=request.data, partial=True)
        else:
            serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, provider=provider)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        provider = self.get_object()
        reviews  = provider.reviews.filter(is_approved=True).order_by('-created_at')[:20]
        return Response(ReviewSerializer(reviews, many=True).data)


class AllReviewsView(generics.ListAPIView):
    """Public endpoint returning recent approved reviews across ALL providers."""
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Review.objects.filter(is_approved=True).select_related('user', 'provider').order_by('-created_at')[:24]

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        data = []
        for r in qs:
            data.append({
                'id': r.id,
                'rating': r.rating,
                'comment': r.comment,
                'created_at': r.created_at.isoformat(),
                'user_name': r.user.get_full_name() or r.user.username or 'Anonymous',
                'provider_id': r.provider.id,
                'provider_name': r.provider.business_name,
                'provider_city': r.provider.city,
            })
        return Response(data)
