import os
import django

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "visitor_manager.settings")

# Setup Django
django.setup()

# Now import and use Django models
from visitors.models import CustomUser
from django.contrib.auth.models import Group

# Get or update the user
try:
    user = CustomUser.objects.get(username='BCHAYAUD')
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"Updated {user.username} as superuser and staff.")

    # Ensure the user is in the admin group
    admin_group, _ = Group.objects.get_or_create(name='admin')
    user.groups.add(admin_group)
    user.save()
    print(f"Added {user.username} to 'admin' group.")
except CustomUser.DoesNotExist:
    print("User 'BCHAYAUD' not found. Creating a new superuser...")
    user = CustomUser.objects.create_superuser(
        username='BCHAYAUD',
        email='bchayaud@sarasotagospeltemple.com',  # Adjust email as needed
        password='your_secure_password'  # Replace with a secure password
    )
    admin_group, _ = Group.objects.get_or_create(name='admin')
    user.groups.add(admin_group)
    user.save()
    print(f"Created superuser {user.username} with admin group.")
except Exception as e:
    print(f"Error updating user: {str(e)}")