from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # List display customization
    list_display = ('username', 'email', 'user_type', 'phone_number', 'show_profile_picture', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('-date_joined',)
    
    # Custom actions
    actions = ['activate_users', 'deactivate_users']
    
    # Fieldsets for editing users
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': (
            'first_name', 
            'last_name', 
            'email', 
            'phone_number', 
            'bio', 
            'date_of_birth', 
            'profile_picture'
        )}),
        ('Permissions', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'user_type',
            'groups',
            'user_permissions'
        )}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Fieldsets for adding new users
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2', 
                'user_type', 'phone_number'
            ),
        }),
    )
    
    def show_profile_picture(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.profile_picture.url
            )
        return "No picture"
    show_profile_picture.short_description = 'Profile Picture'
    
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_users.short_description = "Deactivate selected users"

admin.site.register(CustomUser, CustomUserAdmin)

