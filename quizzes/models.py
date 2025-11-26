import uuid
from django.db import models
from django.contrib.auth.models import User


class Quiz(models.Model):
    """Quiz model for AI-generated and manual quizzes."""

    public_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_quizzes'
    )
    is_ai_generated = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Quizzes"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Question(models.Model):
    """Multiple choice question with 4 options."""

    class CorrectOption(models.TextChoices):
        A = 'A', 'Option A'
        B = 'B', 'Option B'
        C = 'C', 'Option C'
        D = 'D', 'Option D'

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(
        max_length=1,
        choices=CorrectOption.choices
    )
    explanation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.text[:50]}..."


class QuizAttempt(models.Model):
    """Records a user's attempt at a quiz."""

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='quiz_attempts'
    )
    session_key = models.CharField(max_length=40, blank=True)
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    answers = models.JSONField(default=dict)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        user_display = self.user.username if self.user else "Guest"
        return f"{user_display} - {self.quiz.title}"

    @property
    def percentage(self):
        """Calculate the percentage score."""
        if self.total_questions == 0:
            return 0
        return round((self.score / self.total_questions) * 100, 1)


class Notification(models.Model):
    """User notifications for quiz completions and updates."""

    class NotificationType(models.TextChoices):
        QUIZ_COMPLETED = 'quiz_completed', 'Someone completed your quiz'
        QUIZ_SAVED = 'quiz_saved', 'Someone saved your quiz'
        SYSTEM = 'system', 'System notification'

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username}: {self.message[:30]}..."
