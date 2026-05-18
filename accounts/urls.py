from django.urls import path
from .views import login_page, register_page, dashboard_page, admin_panel_page, provider_onboarding_page

urlpatterns = [
    path('login/',        login_page,              name='login'),
    path('register/',     register_page,           name='register'),
    path('dashboard/',    dashboard_page,          name='dashboard'),
    path('admin-panel/',  admin_panel_page,        name='admin-panel'),
    path('provider/onboarding/', provider_onboarding_page, name='provider-onboarding'),
]
