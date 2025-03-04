from django.contrib import admin
from django.utils.html import format_html
from django.templatetags.static import static
from .models import CustomUser, Visitor

# Define ModelAdmin classes first
class CustomUserAdmin(admin.ModelAdmin):
    """Customize the admin interface for CustomUser."""
    list_display = ['username', 'email', 'is_staff', 'is_superuser', 'last_login']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups']
    search_fields = ['username', 'email']
    ordering = ['-last_login']
    filter_horizontal = ['groups', 'user_permissions']  # For better group/permission management


class VisitorAdmin(admin.ModelAdmin):
    """Customize the admin interface for Visitor."""
    list_display = ['name', 'phone', 'address', 'visit_status', 'visit_date']
    list_filter = ['visit_status', 'visit_date', 'visit_request', 'sms_opt_in']
    search_fields = ['name', 'phone', 'address']
    ordering = ['name']
    date_hierarchy = 'visit_date'  # Add date-based navigation for visit_date

# Custom Admin Site Class
class CustomAdminSite(admin.AdminSite):
    site_header = "Sarasota Gospel Temple Administration"
    site_title = "SGT Admin Portal"
    index_title = "Welcome to SGT Admin Panel"

    def get_urls(self):
        """Override get_urls to add custom admin URLs if needed."""
        urls = super().get_urls()
        return urls

    def index(self, request, extra_context=None):
        """Override index to add custom context if needed."""
        extra_context = extra_context or {}
        return super().index(request, extra_context)

    def app_index(self, request, app_label, extra_context=None):
        """Ensure superusers have full access to all apps and models."""
        extra_context = extra_context or {}
        return super().app_index(request, app_label, extra_context)

    def custom_header(self):
        """Custom header with SGT logo."""
        return format_html(
            '<div id="branding"><img src="{}" alt="SGT Logo" height="50px"></div>'.format(
                static('images/logo.png')
            )
        )

    def get_base_context(self, request, extra_context=None):
        """Add custom CSS to the admin interface."""
        context = super().get_base_context(request, extra_context)
        context['extra_css'] = format_html(
            '<link rel="stylesheet" type="text/css" href="{}">'.format(static('css/admin_custom.css'))
        )
        return context

    def has_permission(self, request):
        """Ensure superusers and staff users with permissions can access the admin."""
        return request.user.is_active and (request.user.is_superuser or request.user.is_staff)


# Initialize the custom admin site globally
admin_site = CustomAdminSite(name='custom_admin')

# Register models with the custom admin site
admin_site.register(CustomUser, CustomUserAdmin)
admin_site.register(Visitor, VisitorAdmin)