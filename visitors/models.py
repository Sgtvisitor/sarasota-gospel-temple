from django.db import models
from django.contrib.auth.models import AbstractUser, Group

# Custom User Model
class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser for additional flexibility.
    Uses Django's built-in password hashing via save() override.
    """
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def save(self, *args, **kwargs):
        if self.pk is None or not self.password.startswith('pbkdf2_sha256$'):
            self.set_password(self.password)
        super().save(*args, **kwargs)
        
        # Only hash the password if it's not already hashed (e.g., during creation or update)
        if self.pk is None or not self.password.startswith('pbkdf2_sha256$'):
            self.set_password(self.password)  # Use set_password for secure hashing
        super().save(*args, **kwargs)

# Visitor Model
class Visitor(models.Model):
    """
    Model to store visitor information for Sarasota Gospel Temple.
    Includes basic contact details and visit preferences.
    """
    name = models.CharField(max_length=255, help_text="Full name of the visitor")
    phone = models.CharField(max_length=20, blank=True, help_text="Phone number in E.164 format (e.g., +19415382650)")
    address = models.CharField(max_length=255, blank=True, help_text="Full address (e.g., 3621 Tallevast Rd, Sarasota FL 34243)")
    visit_request = models.CharField(
        max_length=3,
        default="no",
        choices=[('yes', 'Yes'), ('no', 'No')],
        help_text="Indicates if the visitor requests a home visit"
    )
    visit_status = models.CharField(
        max_length=20,
        default="Pending",
        choices=[
            ('Pending', 'Pending'),
            ('Confirmed', 'Confirmed'),
            ('Completed', 'Completed'),
            ('Cancelled', 'Cancelled')
        ],
        help_text="Current status of the visit request"
    )
    visit_date = models.DateField(null=True, blank=True, help_text="Date of the requested visit, if applicable")
    sms_opt_in = models.BooleanField(default=False, help_text="Indicates if the visitor opts in to receive SMS notifications")

    def __str__(self):
        """String representation of the Visitor model."""
        return self.name

    class Meta:
        verbose_name = "Visitor"
        verbose_name_plural = "Visitors"
        ordering = ['name']  # Optional: Order visitors by name in admin

# Role Assignment Function
def assign_role(user, role_name):
    """
    Assign a role (group) to a user. Creates the group if it doesn't exist.
    Args:
        user: The CustomUser instance to assign the role to.
        role_name: String name of the role (group) to assign (e.g., 'admin', 'staff').
    """
    try:
        group, created = Group.objects.get_or_create(name=role_name)
        user.groups.add(group)
        user.save()
        print(f"✅ Role '{role_name}' assigned to user '{user.username}'.")
    except Exception as e:
        print(f"❌ Error assigning role '{role_name}' to user '{user.username}': {str(e)}")