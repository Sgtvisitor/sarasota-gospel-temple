from django.urls import path, include  # Import path and include
from visitors.admin import admin_site  # Import the custom admin site

urlpatterns = [
    path('admin/', admin_site.urls),  # Use custom admin site URLs
    path('', include('visitors.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # Add authentication URLs
    # ... other URL patterns (e.g., for contact, home, etc.)
]