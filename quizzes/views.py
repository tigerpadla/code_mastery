from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Quiz, Question
from .services import QuizGeneratorService


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
        topic = request.POST.get('topic', '').strip()
        
        if not topic:
            messages.error(request, 'Please enter a topic for the quiz.')
            return redirect('home')
        
        if len(topic) > 200:
            messages.error(request, 'Topic is too long. Please use 200 characters or less.')
            return redirect('home')
        
        try:
            # Generate quiz using AI
            service = QuizGeneratorService()
            quiz_data = service.generate_quiz(topic, num_questions=10, difficulty='medium')
            
            if not quiz_data:
                messages.error(
                    request, 
                    'Failed to generate quiz. Please try again with a different topic.'
                )
                return redirect('home')
            
            # Save quiz to database
            with transaction.atomic():
                quiz = Quiz.objects.create(
                    title=quiz_data['title'],
                    description=quiz_data.get('description', ''),
                    creator=request.user if request.user.is_authenticated else None,
                    is_ai_generated=True,
                    is_public=True,
                )
                
                for i, q_data in enumerate(quiz_data['questions']):
                    Question.objects.create(
                        quiz=quiz,
                        text=q_data['text'],
                        option_a=q_data['option_a'],
                        option_b=q_data['option_b'],
                        option_c=q_data['option_c'],
                        option_d=q_data['option_d'],
                        correct_answer=q_data['correct_answer'],
                        explanation=q_data.get('explanation', ''),
                        order=i + 1,
                    )
            
            messages.success(request, f'Quiz "{quiz.title}" generated successfully!')
            return redirect('quizzes:detail', slug=quiz.slug)
            
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('home')
        except Exception as e:
            messages.error(request, 'An error occurred while generating the quiz.')
            return redirect('home')
    
    return redirect('home')


def quiz_detail(request, slug):
    """Display a quiz for taking."""
    quiz = get_object_or_404(Quiz, slug=slug)
    questions = quiz.questions.all()
    
    context = {
        'quiz': quiz,
        'questions': questions,
    }
    return render(request, 'quizzes/quiz_detail.html', context)


def quiz_submit(request, slug):
    """Handle quiz submission and show results."""
    quiz = get_object_or_404(Quiz, slug=slug)
    
    if request.method != 'POST':
        return redirect('quizzes:detail', slug=slug)
    
    questions = quiz.questions.all()
    results = []
    correct_count = 0
    
    for question in questions:
        user_answer = request.POST.get(f'question_{question.id}', '')
        is_correct = user_answer == question.correct_answer
        if is_correct:
            correct_count += 1
        
        results.append({
            'question': question,
            'user_answer': user_answer,
            'is_correct': is_correct,
        })
    
    score_percentage = (correct_count / len(questions) * 100) if questions else 0
    
    context = {
        'quiz': quiz,
        'results': results,
        'correct_count': correct_count,
        'total_questions': len(questions),
        'score_percentage': round(score_percentage),
    }
    return render(request, 'quizzes/quiz_results.html', context)


@login_required
def quiz_create(request):
    """Create a manual quiz."""
    # TODO: Implement manual quiz creation form
    messages.info(request, 'Manual quiz creation coming soon!')
    return redirect('home')

