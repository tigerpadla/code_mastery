import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Extended user profile with avatar and bio."""

    class AvatarChoice(models.TextChoices):
        DEFAULT = 'default', 'Default'
        WIZARD = 'wizard', 'Wizard'
        NINJA = 'ninja', 'Ninja'
        ROBOT = 'robot', 'Robot'
        ASTRONAUT = 'astronaut', 'Astronaut'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.CharField(
        max_length=20,
        choices=AvatarChoice.choices,
        default=AvatarChoice.DEFAULT
    )
    bio = models.TextField(max_length=500, blank=True)
    saved_quizzes = models.ManyToManyField(
        'quizzes.Quiz',
        related_name='saved_by_users',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create Profile when User is created."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Auto-save Profile when User is saved."""
    instance.profile.save()
