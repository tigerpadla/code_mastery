from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Quiz


def home(request):
    """Homepage view with featured quizzes."""
    featured_quizzes = Quiz.objects.filter(
        is_public=True
    ).order_by('-created_at')[:6]
    
    context = {
        'featured_quizzes': featured_quizzes,
    }
    return render(request, 'index.html', context)


def quiz_generate(request):
    """Generate AI quiz from topic."""
    if request.method == 'POST':
        topic = request.POST.get('topic', '')
        if topic:
            # TODO: Implement AI quiz generation
            messages.info(request, f'AI quiz generation for "{topic}" coming soon!')
            return redirect('home')
    
    return redirect('home')


@login_required
def quiz_create(request):
    """Create a manual quiz."""
    # TODO: Implement manual quiz creation form
    messages.info(request, 'Manual quiz creation coming soon!')
    return redirect('home')

