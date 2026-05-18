from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceTypeViewSet, ServiceProviderViewSet, AllReviewsView

router = DefaultRouter()
router.register('types',     ServiceTypeViewSet,     basename='service-types')
router.register('providers', ServiceProviderViewSet, basename='providers')

urlpatterns = [
    path('', include(router.urls)),
    path('reviews/', AllReviewsView.as_view(), name='all-reviews'),
]
