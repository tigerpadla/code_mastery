from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('generate/', views.quiz_generate, name='generate'),
    path('create/', views.quiz_create, name='create'),
]
