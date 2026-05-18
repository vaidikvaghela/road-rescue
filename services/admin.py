from django.contrib import admin
from django.utils.html import format_html
from .models import ServiceType, ServiceProvider, Review


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display  = ['icon', 'name', 'is_active']
    list_editable = ['is_active']
    search_fields = ['name']


class ReviewInline(admin.TabularInline):
    model        = Review
    extra        = 0
    readonly_fields = ['user', 'rating', 'comment', 'created_at']
    can_delete   = False


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display    = ['business_name', 'city', 'status_badge', 'is_available', 'rating_display', 'total_reviews', 'base_fee', 'created_at']
    list_filter     = ['status', 'is_available', 'is_24_7', 'city']
    search_fields   = ['business_name', 'city', 'phone', 'email']
    list_editable   = ['is_available']
    readonly_fields = ['rating', 'total_reviews', 'total_jobs', 'created_at', 'updated_at']
    filter_horizontal = ['service_types']
    inlines         = [ReviewInline]

    fieldsets = (
        ('Business Info',  {'fields': ('user', 'business_name', 'description', 'logo', 'service_types')}),
        ('Contact',        {'fields': ('phone', 'email', 'address', 'city', 'state', 'pincode')}),
        ('Location',       {'fields': ('latitude', 'longitude')}),
        ('Operations',     {'fields': ('opening_time', 'closing_time', 'is_24_7', 'base_fee', 'is_available')}),
        ('Status & Stats', {'fields': ('status', 'rating', 'total_reviews', 'total_jobs')}),
        ('Timestamps',     {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    actions = ['approve_providers', 'suspend_providers']

    def status_badge(self, obj):
        colors = {'active': '#22c55e', 'inactive': '#6b7280', 'suspended': '#ef4444', 'pending': '#f97316'}
        c = colors.get(obj.status, '#6b7280')
        return format_html('<span style="background:{};color:#fff;padding:3px 10px;border-radius:20px;font-size:0.78rem;font-weight:600;">{}</span>', c, obj.get_status_display())
    status_badge.short_description = 'Status'

    def rating_display(self, obj):
        return format_html('<span style="color:#f97316;">{}</span> <strong>{}</strong>', '★' * int(obj.rating) + '☆' * (5 - int(obj.rating)), obj.rating)
    rating_display.short_description = 'Rating'

    def approve_providers(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, f'{queryset.count()} provider(s) approved.')
    approve_providers.short_description = '✅ Approve selected providers'

    def suspend_providers(self, request, queryset):
        queryset.update(status='suspended')
        self.message_user(request, f'{queryset.count()} provider(s) suspended.')
    suspend_providers.short_description = '🚫 Suspend selected providers'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ['user', 'provider', 'rating', 'is_approved', 'created_at']
    list_filter   = ['rating', 'is_approved']
    list_editable = ['is_approved']
    search_fields = ['user__email', 'provider__business_name']
