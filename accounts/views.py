from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Avg
from .models import Profile


@login_required
def profile_view(request, username=None):
    """Display user profile."""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    profile = user.profile
    created_quizzes = user.created_quizzes.filter(is_public=True).order_by('-created_at')[:6]
    saved_quizzes = profile.saved_quizzes.all().order_by('-created_at')[:6]
    
    # Check if viewing own profile
    is_own_profile = request.user == user
    
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
        'total_created': user.created_quizzes.filter(is_public=True).count(),
        'total_saved': profile.saved_quizzes.count(),
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
    from quizzes.models import Quiz
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    profile = request.user.profile
    
    if quiz in profile.saved_quizzes.all():
        profile.saved_quizzes.remove(quiz)
        messages.info(request, f'"{quiz.title}" removed from saved quizzes.')
    else:
        profile.saved_quizzes.add(quiz)
        messages.success(request, f'"{quiz.title}" saved to your profile!')
    
    # Redirect back to the previous page
    return redirect(request.META.get('HTTP_REFERER', 'home'))
