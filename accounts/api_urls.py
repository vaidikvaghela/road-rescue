from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, ProfileView, ChangePasswordView, AdminStatsView, AdminExportView, ProviderOnboardingView, AdminActionView

urlpatterns = [
    path('register/',             RegisterView.as_view(),         name='api-register'),
    path('login/',                LoginView.as_view(),             name='api-login'),
    path('token/refresh/',        TokenRefreshView.as_view(),      name='token-refresh'),
    path('profile/',              ProfileView.as_view(),           name='api-profile'),
    path('change-password/',      ChangePasswordView.as_view(),    name='change-password'),
    path('provider/profile/',     ProviderOnboardingView.as_view(),name='provider-onboarding-api'),
    path('admin/stats/',          AdminStatsView.as_view(),        name='admin-stats'),
    path('admin/export/',         AdminExportView.as_view(),       name='admin-export'),
    path('admin/action/',         AdminActionView.as_view(),       name='admin-action'),
]
