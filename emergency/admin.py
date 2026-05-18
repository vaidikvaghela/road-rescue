from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import EmergencyRequest, Dispatch


class DispatchInline(admin.StackedInline):
    model           = Dispatch
    extra           = 0
    readonly_fields = ['dispatched_at']


@admin.register(EmergencyRequest)
class EmergencyRequestAdmin(admin.ModelAdmin):
    list_display  = ['req_id', 'requester_name', 'requester_phone', 'issue_badge', 'priority_badge', 'status_badge', 'assigned_provider', 'created_at']
    list_filter   = ['status', 'priority', 'issue_type', 'vehicle_type']
    search_fields = ['requester_name', 'requester_phone', 'location_address']
    readonly_fields = ['created_at', 'updated_at', 'assigned_at', 'completed_at']
    inlines       = [DispatchInline]
    date_hierarchy= 'created_at'

    fieldsets = (
        ('Requester',  {'fields': ('user', 'requester_name', 'requester_phone')}),
        ('Incident',   {'fields': ('vehicle_type', 'issue_type', 'notes', 'priority')}),
        ('Location',   {'fields': ('location_address', 'latitude', 'longitude')}),
        ('Assignment', {'fields': ('assigned_provider', 'status', 'estimated_arrival')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'assigned_at', 'completed_at'), 'classes': ('collapse',)}),
    )

    actions = ['mark_assigned', 'mark_en_route', 'mark_completed', 'mark_cancelled', 'mark_critical']

    def req_id(self, obj):
        return format_html('<strong style="color:#f97316;">#{}</strong>', obj.pk)
    req_id.short_description = 'ID'

    def status_badge(self, obj):
        colors = {'pending':'#f97316','assigned':'#3b82f6','en_route':'#8b5cf6','in_progress':'#f59e0b','completed':'#22c55e','cancelled':'#ef4444'}
        c = colors.get(obj.status, '#6b7280')
        return format_html('<span style="background:{};color:#fff;padding:3px 10px;border-radius:20px;font-size:0.78rem;font-weight:600;">{}</span>', c, obj.get_status_display())
    status_badge.short_description = 'Status'

    def priority_badge(self, obj):
        colors = {'low':'#6b7280','medium':'#f59e0b','high':'#f97316','critical':'#ef4444'}
        return format_html('<span style="color:{};font-weight:700;">{}</span>', colors.get(obj.priority,'#6b7280'), obj.get_priority_display())
    priority_badge.short_description = 'Priority'

    def issue_badge(self, obj):
        icons = {'flat_tyre':'🛞','engine_failure':'⚙️','battery_dead':'🔋','accident':'💥','out_of_fuel':'⛽','overheating':'🌡️','electrical':'⚡','other':'❓'}
        return format_html('{} {}', icons.get(obj.issue_type,'❓'), obj.get_issue_type_display())
    issue_badge.short_description = 'Issue'

    def mark_assigned(self, request, queryset):
        queryset.update(status='assigned', assigned_at=timezone.now())
        self.message_user(request, f'{queryset.count()} marked as Assigned.')
    mark_assigned.short_description = '📋 Mark Assigned'

    def mark_en_route(self, request, queryset):
        queryset.update(status='en_route')
        self.message_user(request, f'{queryset.count()} marked as En Route.')
    mark_en_route.short_description = '🚗 Mark En Route'

    def mark_completed(self, request, queryset):
        queryset.update(status='completed', completed_at=timezone.now())
        self.message_user(request, f'{queryset.count()} marked as Completed.')
    mark_completed.short_description = '✅ Mark Completed'

    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f'{queryset.count()} marked as Cancelled.')
    mark_cancelled.short_description = '❌ Mark Cancelled'

    def mark_critical(self, request, queryset):
        queryset.update(priority='critical')
        self.message_user(request, f'{queryset.count()} set to Critical.')
    mark_critical.short_description = '🔴 Set Critical'


@admin.register(Dispatch)
class DispatchAdmin(admin.ModelAdmin):
    list_display  = ['request', 'technician_name', 'technician_phone', 'vehicle_number', 'dispatched_at']
    search_fields = ['technician_name', 'technician_phone']
    readonly_fields = ['dispatched_at']


from .models import ServiceRequest

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display  = ['sr_id', 'customer', 'provider', 'service_type_text', 'vehicle_type', 'status_badge', 'created_at']
    list_filter   = ['status', 'vehicle_type']
    search_fields = ['customer__email', 'provider__business_name', 'service_type_text', 'vehicle_reg_no']
    readonly_fields = ['created_at', 'updated_at', 'accepted_at', 'completed_at']

    def sr_id(self, obj):
        return format_html('<strong style="color:#a78bfa;">SR#{}</strong>', obj.pk)
    sr_id.short_description = 'ID'

    def status_badge(self, obj):
        colors = {
            'pending':     '#f97316',
            'accepted':    '#3b82f6',
            'declined':    '#ef4444',
            'in_progress': '#f59e0b',
            'completed':   '#22c55e',
            'cancelled':   '#6b7280',
        }
        c = colors.get(obj.status, '#6b7280')
        return format_html('<span style="background:{};color:#fff;padding:3px 10px;border-radius:20px;font-size:0.78rem;font-weight:600;">{}</span>', c, obj.get_status_display())
    status_badge.short_description = 'Status'

