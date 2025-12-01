from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import UserCustom
from allauth.socialaccount.models import SocialAccount


class SocialProviderFilter(admin.SimpleListFilter):
    title = 'Login Origin'
    parameter_name = 'origin'

    def lookups(self, request, model_admin):
        return [
            ('local', 'Local'),
            ('google', 'Google'),
            ('github', 'GitHub'),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'local':
            return queryset.filter(socialaccount__isnull=True)
        if value in ('google', 'github'):
            return queryset.filter(socialaccount__provider=value)
        return queryset


@admin.register(UserCustom)
class UserCustomAdmin(UserAdmin):
    list_display = (
        'username', 'get_full_name', 'email', 'phone', 'role', 'gender',
        'login_origin', 'is_active', 'is_staff', 'created_at', 'profile_image_preview'
    )
    
    list_filter = (
        'role', 'gender', 'is_active', 'is_staff', 'is_superuser',
        'created_at', 'updated_at', SocialProviderFilter,
    )
    
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    ordering = ('-created_at',)
    list_editable = ('is_active', 'role')
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined', 'profile_image_preview')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('username', 'first_name', 'last_name', 'email', 'phone', 'birthday', 'gender')
        }),
        ('Profile Image', {
            'fields': ('image_profile', 'profile_image_preview'),
            'classes': ('collapse',)
        }),
        ('Permissions & Roles', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Password', {
            'fields': ('password',),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Basic Information', {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2')
        }),
        ('Additional Information', {
            'classes': ('wide', 'collapse'),
            'fields': ('birthday', 'gender', 'image_profile', 'role')
        }),
        ('Permissions', {
            'classes': ('wide', 'collapse'),
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
    )
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'first_name'
    
    def profile_image_preview(self, obj):
        if obj.image_profile:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;" />',
                obj.image_profile.url
            )
        return "No image"
    profile_image_preview.short_description = 'Preview'

    def login_origin(self, obj):
        providers = list(obj.socialaccount_set.values_list('provider', flat=True))
        if not providers:
            return 'Local'
        return ', '.join(p.capitalize() for p in providers)
    login_origin.short_description = 'Origin'
    
    actions = ['activate_users', 'deactivate_users', 'make_admin', 'make_client']
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated')
    activate_users.short_description = "Activate users"
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated')
    deactivate_users.short_description = "Deactivate users"
    
    def make_admin(self, request, queryset):
        updated = queryset.update(role='admin')
        self.message_user(request, f'{updated} user(s) converted to admin')
    make_admin.short_description = "Make administrators"
    
    def make_client(self, request, queryset):
        updated = queryset.update(role='client')
        self.message_user(request, f'{updated} user(s) converted to client')
    make_client.short_description = "Make clients"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related().prefetch_related('groups', 'user_permissions', 'socialaccount_set')
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'role') and request.user.role in ['admin', 'root']:
            return True
        return obj == request.user


admin.site.site_header = "BilZapp Administration"
admin.site.site_title = "BilZapp Admin"
admin.site.index_title = "Welcome to BilZapp Administration"
