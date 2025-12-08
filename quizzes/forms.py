from django import forms
from .models import Quiz, Question


class QuizForm(forms.ModelForm):
    """Form for creating/editing a quiz."""

    class Meta:
        model = Quiz
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter quiz title...',
                'maxlength': '200',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a brief description of your quiz (optional)...',
                'rows': 3,
            }),
        }
        labels = {
            'title': 'Quiz Title',
            'description': 'Description',
        }


class QuestionForm(forms.ModelForm):
    """Form for creating/editing a question."""

    class Meta:
        model = Question
        fields = [
            'text',
            'option_a',
            'option_b',
            'option_c',
            'option_d',
            'correct_answer',
            'explanation']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your question...',
                'rows': 2,
            }),
            'option_a': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option A',
            }),
            'option_b': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option B',
            }),
            'option_c': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option C',
            }),
            'option_d': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option D',
            }),
            'correct_answer': forms.Select(attrs={
                'class': 'form-select',
            }),
            'explanation': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Explain the correct answer (optional)...',
                'rows': 2,
            }),
        }
        labels = {
            'text': 'Question',
            'option_a': 'Option A',
            'option_b': 'Option B',
            'option_c': 'Option C',
            'option_d': 'Option D',
            'correct_answer': 'Correct Answer',
            'explanation': 'Explanation',
        }


# Formset for handling multiple questions
QuestionFormSet = forms.inlineformset_factory(
    Quiz,
    Question,
    form=QuestionForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
