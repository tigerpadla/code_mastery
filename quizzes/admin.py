from django.contrib import admin
from .models import Quiz, Question, QuizAttempt, Notification


class QuestionInline(admin.TabularInline):
    """Inline admin for adding questions to quizzes."""
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin configuration for Quiz model."""
    list_display = ('title', 'slug', 'creator', 'is_ai_generated', 'is_featured', 'created_at')
    list_filter = ('is_ai_generated', 'is_featured', 'created_at')
    list_editable = ('is_featured',)
    search_fields = ('title', 'description', 'creator__username', 'slug')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin configuration for Question model."""
    list_display = ('quiz', 'text', 'correct_answer', 'order')
    list_filter = ('quiz', 'correct_answer')
    search_fields = ('text', 'quiz__title')


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    """Admin configuration for QuizAttempt model."""
    list_display = ('quiz', 'user', 'score', 'total_questions', 'started_at', 'completed_at')
    list_filter = ('quiz', 'started_at', 'completed_at')
    search_fields = ('quiz__title', 'user__username')
    readonly_fields = ('started_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification model."""
    list_display = ('recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'message')
    readonly_fields = ('created_at',)
