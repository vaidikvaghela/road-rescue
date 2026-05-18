from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmergencyRequestViewSet, ServiceRequestViewSet, PushSubscriptionViewSet

router = DefaultRouter()
router.register('requests', EmergencyRequestViewSet,  basename='emergency-requests')
router.register('service-requests', ServiceRequestViewSet, basename='service-requests')
router.register('push', PushSubscriptionViewSet, basename='push')


urlpatterns = [path('', include(router.urls))]
