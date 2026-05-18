from django.contrib.admin import AdminSite
from django.db.models import Avg


class RoadRescueAdminSite(AdminSite):
    site_header = "RoadRescue Admin"
    site_title  = "RoadRescue Portal"
    index_title = "Vehicle Breakdown Management"

    def index(self, request, extra_context=None):
        from accounts.models import User
        from services.models import ServiceProvider, Review
        from emergency.models import EmergencyRequest
        from django.utils import timezone

        today = timezone.now().date()
        extra_context = extra_context or {}
        extra_context.update({
            'total_users':      User.objects.count(),
            'total_providers':  ServiceProvider.objects.filter(status='active').count(),
            'pending_requests': EmergencyRequest.objects.filter(status='pending').count(),
            'completed_today':  EmergencyRequest.objects.filter(status='completed', completed_at__date=today).count(),
            'avg_rating':       round(Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0, 1),
            'recent_requests':  EmergencyRequest.objects.order_by('-created_at')[:8],
            'pending_providers':ServiceProvider.objects.filter(status='pending').order_by('-created_at')[:5],
        })
        return super().index(request, extra_context)
