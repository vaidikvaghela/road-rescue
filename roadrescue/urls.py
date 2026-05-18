from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('sw.js',           TemplateView.as_view(template_name='sw.js', content_type='application/javascript'), name='sw.js'),
    path('admin/',          admin.site.urls),
    path('',                include('core.urls')),
    path('',                include('accounts.urls')),
    path('api/v1/auth/',    include('accounts.api_urls')),
    path('api/v1/services/',include('services.urls')),
    path('api/v1/emergency/',include('emergency.urls')),
    path('api/schema/',     SpectacularAPIView.as_view(),                        name='schema'),
    path('api/docs/',       SpectacularSwaggerView.as_view(url_name='schema'),   name='swagger-ui'),
    path('api/redoc/',      SpectacularRedocView.as_view(url_name='schema'),     name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
