from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group

@receiver(post_migrate)
def create_groups(sender, **kwargs):
    if sender.name == "visitors":
        Group.objects.get_or_create(name="Admin")
        Group.objects.get_or_create(name="Staff")
