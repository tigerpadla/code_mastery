from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField


class Profile(models.Model):
    """Extended user profile with avatar and bio."""

    class AvatarChoice(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
        CUSTOM = 'custom', 'Custom'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.CharField(
        max_length=20,
        choices=AvatarChoice.choices,
        default=AvatarChoice.MALE
    )
    custom_avatar = CloudinaryField(
        'image',
        blank=True,
        null=True,
        folder='code_mastery/avatars',
        transformation={'width': 200, 'height': 200, 'crop': 'fill', 'gravity': 'face'}
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

    def get_avatar_url(self):
        """Return the appropriate avatar URL based on choice."""
        if self.avatar == self.AvatarChoice.CUSTOM and self.custom_avatar:
            return self.custom_avatar.url
        elif self.avatar == self.AvatarChoice.FEMALE:
            return '/static/images/user-female-icon.png'
        else:
            return '/static/images/user-male-icon.png'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create Profile when User is created."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Auto-save Profile when User is saved."""
    instance.profile.save()
