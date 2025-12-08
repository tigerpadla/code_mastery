from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg
from .models import Profile
from quizzes.models import Quiz, QuizAttempt, Notification


def profile_view(request, username=None):
    """Display user profile. Public profiles are viewable by anyone."""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        # Viewing own profile requires login
        if not request.user.is_authenticated:
            return redirect('account_login')
        user = request.user
    
    profile = user.profile
    created_quizzes = user.created_quizzes.all().order_by('-created_at')[:6]
    
    # Check if viewing own profile
    is_own_profile = request.user.is_authenticated and request.user == user
    
    # Only show saved quizzes on own profile
    saved_quizzes = profile.saved_quizzes.all().order_by('-created_at')[:6] if is_own_profile else []
    
    # Calculate quiz attempt stats
    quiz_attempts = user.quiz_attempts.all()
    total_attempts = quiz_attempts.count()
    
    # Calculate average score percentage
    if total_attempts > 0:
        avg_score = quiz_attempts.aggregate(
            avg=Avg('score') 
        )['avg'] or 0
        avg_total = quiz_attempts.aggregate(
            avg=Avg('total_questions')
        )['avg'] or 1
        avg_percentage = round((avg_score / avg_total) * 100) if avg_total > 0 else 0
    else:
        avg_percentage = 0
    
    context = {
        'profile_user': user,
        'profile': profile,
        'created_quizzes': created_quizzes,
        'saved_quizzes': saved_quizzes,
        'is_own_profile': is_own_profile,
        'total_created': user.created_quizzes.count(),
        'total_saved': profile.saved_quizzes.count() if is_own_profile else 0,
        'total_attempts': total_attempts,
        'avg_percentage': avg_percentage,
    }
    return render(request, 'account/profile.html', context)


@login_required
def profile_edit(request):
    """Edit user profile."""
    profile = request.user.profile
    
    if request.method == 'POST':
        # Update bio
        bio = request.POST.get('bio', '').strip()
        if len(bio) <= 500:
            profile.bio = bio
        
        # Update avatar choice
        avatar_choice = request.POST.get('avatar', 'male')
        if avatar_choice in ['male', 'female', 'custom']:
            profile.avatar = avatar_choice
        
        # Handle custom avatar upload
        if 'custom_avatar' in request.FILES:
            profile.custom_avatar = request.FILES['custom_avatar']
            profile.avatar = 'custom'
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    context = {
        'profile': profile,
    }
    return render(request, 'account/profile_edit.html', context)


@login_required
def save_quiz(request, quiz_id):
    """Save/unsave a quiz to user's profile."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    profile = request.user.profile
    
    is_saved = quiz in profile.saved_quizzes.all()
    
    if is_saved:
        profile.saved_quizzes.remove(quiz)
        message = f'"{quiz.title}" removed from saved quizzes.'
        is_saved = False
    else:
        profile.saved_quizzes.add(quiz)
        message = f'"{quiz.title}" saved to your profile!'
        is_saved = True
        
        # Notify quiz creator (if not self)
        if quiz.creator and quiz.creator != request.user:
            Notification.objects.create(
                recipient=quiz.creator,
                notification_type=Notification.NotificationType.QUIZ_SAVED,
                message=f'{request.user.username} saved your quiz "{quiz.title}"',
                related_quiz=quiz,
            )
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'saved': is_saved,
            'message': message
        })
    
    # Regular request - redirect with message
    if is_saved:
        messages.success(request, message)
    else:
        messages.info(request, message)
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def quiz_history(request):
    """Display user's quiz attempt history."""
    attempts = QuizAttempt.objects.filter(user=request.user).select_related('quiz')
    
    context = {
        'attempts': attempts,
    }
    return render(request, 'account/quiz_history.html', context)


@login_required
def attempt_detail(request, attempt_id):
    """Display detailed view of a quiz attempt."""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    questions = attempt.quiz.questions.all()
    
    # Build results with user's answers
    results = []
    for question in questions:
        user_answer = attempt.answers.get(str(question.id), '')
        is_correct = user_answer == question.correct_answer
        results.append({
            'question': question,
            'user_answer': user_answer,
            'is_correct': is_correct,
        })
    
    context = {
        'attempt': attempt,
        'quiz': attempt.quiz,
        'results': results,
        'correct_count': attempt.score,
        'total_questions': attempt.total_questions,
        'score_percentage': attempt.percentage,
    }
    return render(request, 'account/attempt_detail.html', context)


@login_required
def notifications_list(request):
    """Display all notifications for the current user."""
    notifications = Notification.objects.filter(recipient=request.user)
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'account/notifications.html', context)


@login_required
def notification_mark_read(request, notification_id=None):
    """Mark a single notification or all notifications as read."""
    if request.method != 'POST':
        return redirect('accounts:notifications')
    
    if notification_id:
        # Mark single notification as read
        notification = get_object_or_404(
            Notification, id=notification_id, recipient=request.user
        )
        notification.is_read = True
        notification.save()
    else:
        # Mark all notifications as read
        Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('accounts:notifications')


@login_required
def my_quizzes(request):
    """Display all quizzes created by the current user."""
    quizzes = request.user.created_quizzes.all().order_by('-created_at')
    
    context = {
        'quizzes': quizzes,
        'page_title': 'My Quizzes',
        'empty_message': 'You haven\'t created any quizzes yet.',
        'empty_icon': 'fa-pen-fancy',
        'show_create_btn': True,
    }
    return render(request, 'account/quiz_list.html', context)


@login_required
def saved_quizzes(request):
    """Display all quizzes saved by the current user."""
    quizzes = request.user.profile.saved_quizzes.all().order_by('-created_at')
    
    context = {
        'quizzes': quizzes,
        'page_title': 'Saved Quizzes',
        'empty_message': 'You haven\'t saved any quizzes yet.',
        'empty_icon': 'fa-bookmark',
        'show_unsave_btn': True,
    }
    return render(request, 'account/quiz_list.html', context)
