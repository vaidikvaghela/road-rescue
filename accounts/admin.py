from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display    = ['email','get_full_name','role','phone','is_verified','is_active','created_at']
    list_filter     = ['role','is_verified','is_active','is_staff']
    search_fields   = ['email','first_name','last_name','phone']
    ordering        = ['-created_at']
    readonly_fields = ['created_at','updated_at']

    fieldsets = (
        ('Login',      {'fields': ('email','username','password')}),
        ('Personal',   {'fields': ('first_name','last_name','phone','profile_picture')}),
        ('Role',       {'fields': ('role','is_verified','is_active','is_staff','is_superuser')}),
        ('Timestamps', {'fields': ('created_at','updated_at'), 'classes': ('collapse',)}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email','username','first_name','last_name','role','password1','password2')}),
    )
