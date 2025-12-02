from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('generate/', views.quiz_generate, name='generate'),
    path('create/', views.quiz_create, name='create'),
    path('<slug:slug>/', views.quiz_detail, name='detail'),
    path('<slug:slug>/submit/', views.quiz_submit, name='submit'),
    path('<slug:slug>/edit/', views.quiz_edit, name='edit'),
    path('<slug:slug>/delete/', views.quiz_delete, name='delete'),
]
