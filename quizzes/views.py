from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Quiz, Question
from .services import QuizGeneratorService


def home(request):
    """Homepage view with featured quizzes."""
    featured_quizzes = Quiz.objects.all().order_by('-created_at')[:6]
    
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
    from .models import QuizAttempt
    from django.utils import timezone
    
    quiz = get_object_or_404(Quiz, slug=slug)
    
    if request.method != 'POST':
        return redirect('quizzes:detail', slug=slug)
    
    questions = quiz.questions.all()
    results = []
    correct_count = 0
    answers_dict = {}
    
    for question in questions:
        user_answer = request.POST.get(f'question_{question.id}', '')
        is_correct = user_answer == question.correct_answer
        if is_correct:
            correct_count += 1
        
        # Store answer for QuizAttempt
        answers_dict[str(question.id)] = user_answer
        
        results.append({
            'question': question,
            'user_answer': user_answer,
            'is_correct': is_correct,
        })
    
    score_percentage = (correct_count / len(questions) * 100) if questions else 0
    
    # Save quiz attempt for logged-in users
    if request.user.is_authenticated:
        QuizAttempt.objects.create(
            quiz=quiz,
            user=request.user,
            score=correct_count,
            total_questions=len(questions),
            answers=answers_dict,
            completed_at=timezone.now(),
        )
    
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
    from .forms import QuizForm, QuestionFormSet
    
    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        
        if quiz_form.is_valid():
            # Save quiz first
            quiz = quiz_form.save(commit=False)
            quiz.creator = request.user
            quiz.is_ai_generated = False
            quiz.save()
            
            # Now handle questions formset
            question_formset = QuestionFormSet(request.POST, instance=quiz)
            
            if question_formset.is_valid():
                questions = question_formset.save(commit=False)
                for i, question in enumerate(questions):
                    question.order = i + 1
                    question.save()
                
                # Delete any marked for deletion
                for obj in question_formset.deleted_objects:
                    obj.delete()
                
                messages.success(request, f'Quiz "{quiz.title}" created successfully!')
                return redirect('quizzes:detail', slug=quiz.slug)
            else:
                # If questions are invalid, delete the quiz we just created
                quiz.delete()
                messages.error(request, 'Please fix the errors in your questions.')
        else:
            question_formset = QuestionFormSet(request.POST)
    else:
        quiz_form = QuizForm()
        question_formset = QuestionFormSet()
    
    context = {
        'quiz_form': quiz_form,
        'question_formset': question_formset,
    }
    return render(request, 'quizzes/quiz_create.html', context)


@login_required
def quiz_edit(request, slug):
    """Edit an existing quiz."""
    from .forms import QuizForm, QuestionFormSet
    
    quiz = get_object_or_404(Quiz, slug=slug)
    
    # Only allow creator to edit
    if quiz.creator != request.user:
        messages.error(request, 'You can only edit your own quizzes.')
        return redirect('quizzes:detail', slug=slug)
    
    if request.method == 'POST':
        quiz_form = QuizForm(request.POST, instance=quiz)
        question_formset = QuestionFormSet(request.POST, instance=quiz)
        
        if quiz_form.is_valid() and question_formset.is_valid():
            quiz_form.save()
            
            questions = question_formset.save(commit=False)
            for i, question in enumerate(questions):
                question.order = i + 1
                question.save()
            
            for obj in question_formset.deleted_objects:
                obj.delete()
            
            messages.success(request, f'Quiz "{quiz.title}" updated successfully!')
            return redirect('quizzes:detail', slug=quiz.slug)
    else:
        quiz_form = QuizForm(instance=quiz)
        question_formset = QuestionFormSet(instance=quiz)
    
    context = {
        'quiz': quiz,
        'quiz_form': quiz_form,
        'question_formset': question_formset,
        'is_edit': True,
    }
    return render(request, 'quizzes/quiz_create.html', context)


@login_required
def quiz_delete(request, slug):
    """Delete a quiz."""
    quiz = get_object_or_404(Quiz, slug=slug)
    
    # Only allow creator to delete
    if quiz.creator != request.user:
        messages.error(request, 'You can only delete your own quizzes.')
        return redirect('quizzes:detail', slug=slug)
    
    if request.method == 'POST':
        title = quiz.title
        quiz.delete()
        messages.success(request, f'Quiz "{title}" deleted successfully!')
        return redirect('home')
    
    return redirect('quizzes:detail', slug=slug)


