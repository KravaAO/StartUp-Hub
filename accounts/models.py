from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Shared user model, ready for future extension."""
