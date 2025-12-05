from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile_view, name='profile_user'),
    path('quiz/<int:quiz_id>/save/', views.save_quiz, name='save_quiz'),
    path('history/', views.quiz_history, name='quiz_history'),
    path('history/<int:attempt_id>/', views.attempt_detail, name='attempt_detail'),
    path('notifications/', views.notifications_list, name='notifications'),
    path('notifications/mark-read/', views.notification_mark_read, name='notifications_mark_all_read'),
    path('notifications/<int:notification_id>/read/', views.notification_mark_read, name='notification_mark_read'),
]
