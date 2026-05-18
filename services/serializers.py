from rest_framework import serializers
from .models import ServiceType, ServiceProvider, Review


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ServiceType
        fields = ['id', 'name', 'description', 'icon']


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model        = Review
        fields       = ['id', 'user', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class ServiceProviderListSerializer(serializers.ModelSerializer):
    service_types      = ServiceTypeSerializer(many=True, read_only=True)
    distance           = serializers.FloatField(read_only=True, default=None)
    service_type_display = serializers.SerializerMethodField()

    def get_service_type_display(self, obj):
        types = obj.service_types.all()
        if types.exists():
            return ', '.join(t.name for t in types)
        return 'General Service'

    class Meta:
        model  = ServiceProvider
        fields = [
            'id', 'business_name', 'service_types', 'service_type_display',
            'city', 'phone', 'is_available', 'is_24_7', 'base_fee',
            'rating', 'total_reviews', 'distance', 'logo',
            'latitude', 'longitude',
        ]


class ServiceProviderSerializer(serializers.ModelSerializer):
    service_types = ServiceTypeSerializer(many=True, read_only=True)
    reviews       = ReviewSerializer(many=True, read_only=True)
    distance      = serializers.FloatField(read_only=True, default=None)

    class Meta:
        model  = ServiceProvider
        fields = ['id', 'business_name', 'description', 'service_types', 'phone', 'email', 'address', 'city', 'state', 'pincode', 'latitude', 'longitude', 'opening_time', 'closing_time', 'is_24_7', 'base_fee', 'is_available', 'logo', 'rating', 'total_reviews', 'total_jobs', 'distance', 'reviews']
