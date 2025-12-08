"""
Tests for the quizzes app.
Tests cover models, views, and templates.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Quiz, Question, QuizAttempt, Notification


class QuizModelTest(TestCase):
    """Test cases for the Quiz model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_quiz_creation(self):
        """Test that a quiz can be created."""
        quiz = Quiz.objects.create(
            title='Python Basics',
            description='Test your Python knowledge',
            creator=self.user
        )
        self.assertEqual(quiz.title, 'Python Basics')
        self.assertEqual(quiz.creator, self.user)

    def test_quiz_str_method(self):
        """Test the Quiz string representation."""
        quiz = Quiz.objects.create(title='Test Quiz')
        self.assertEqual(str(quiz), 'Test Quiz')

    def test_quiz_slug_auto_generated(self):
        """Test that slug is automatically generated from title."""
        quiz = Quiz.objects.create(title='Python Basics Quiz')
        self.assertEqual(quiz.slug, 'python-basics-quiz')

    def test_quiz_slug_unique(self):
        """Test that duplicate titles get unique slugs."""
        quiz1 = Quiz.objects.create(title='Python Quiz')
        quiz2 = Quiz.objects.create(title='Python Quiz')
        self.assertNotEqual(quiz1.slug, quiz2.slug)
        self.assertEqual(quiz2.slug, 'python-quiz-1')

    def test_quiz_default_values(self):
        """Test quiz default values."""
        quiz = Quiz.objects.create(title='Test Quiz')
        self.assertFalse(quiz.is_ai_generated)
        self.assertFalse(quiz.is_featured)

    def test_quiz_ordering(self):
        """Test that quizzes are ordered by created_at descending."""
        quiz1 = Quiz.objects.create(title='First Quiz')
        quiz2 = Quiz.objects.create(title='Second Quiz')
        quizzes = Quiz.objects.all()
        self.assertEqual(quizzes[0], quiz2)
        self.assertEqual(quizzes[1], quiz1)


class QuestionModelTest(TestCase):
    """Test cases for the Question model."""

    def setUp(self):
        """Set up test data."""
        self.quiz = Quiz.objects.create(title='Test Quiz')

    def test_question_creation(self):
        """Test that a question can be created."""
        question = Question.objects.create(
            quiz=self.quiz,
            text='What is Python?',
            option_a='A programming language',
            option_b='A snake',
            option_c='A movie',
            option_d='A game',
            correct_answer='A',
            order=1
        )
        self.assertEqual(question.text, 'What is Python?')
        self.assertEqual(question.correct_answer, 'A')

    def test_question_str_method(self):
        """Test the Question string representation."""
        question = Question.objects.create(
            quiz=self.quiz,
            text='What is the output of print("Hello")?',
            option_a='Hello',
            option_b='Error',
            option_c='None',
            option_d='print',
            correct_answer='A',
            order=1
        )
        self.assertIn('Q1:', str(question))

    def test_question_ordering(self):
        """Test that questions are ordered by order field."""
        q2 = Question.objects.create(
            quiz=self.quiz, text='Q2', option_a='A', option_b='B',
            option_c='C', option_d='D', correct_answer='A', order=2
        )
        q1 = Question.objects.create(
            quiz=self.quiz, text='Q1', option_a='A', option_b='B',
            option_c='C', option_d='D', correct_answer='A', order=1
        )
        questions = self.quiz.questions.all()
        self.assertEqual(questions[0], q1)
        self.assertEqual(questions[1], q2)


class QuizAttemptModelTest(TestCase):
    """Test cases for the QuizAttempt model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.quiz = Quiz.objects.create(title='Test Quiz')

    def test_quiz_attempt_creation(self):
        """Test that a quiz attempt can be created."""
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            score=8,
            total_questions=10
        )
        self.assertEqual(attempt.score, 8)
        self.assertEqual(attempt.total_questions, 10)

    def test_quiz_attempt_str_method(self):
        """Test the QuizAttempt string representation."""
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            score=8,
            total_questions=10
        )
        self.assertIn('testuser', str(attempt))
        self.assertIn('Test Quiz', str(attempt))

    def test_quiz_attempt_percentage(self):
        """Test the percentage property calculation."""
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            score=8,
            total_questions=10
        )
        self.assertEqual(attempt.percentage, 80.0)

    def test_quiz_attempt_percentage_zero_questions(self):
        """Test percentage returns 0 when total_questions is 0."""
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            score=0,
            total_questions=0
        )
        self.assertEqual(attempt.percentage, 0)

    def test_quiz_attempt_guest_user(self):
        """Test quiz attempt can be created without user."""
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            session_key='abc123',
            score=5,
            total_questions=10
        )
        self.assertIsNone(attempt.user)
        self.assertIn('Guest', str(attempt))


class NotificationModelTest(TestCase):
    """Test cases for the Notification model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.quiz = Quiz.objects.create(title='Test Quiz')

    def test_notification_creation(self):
        """Test that a notification can be created."""
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type='quiz_completed',
            message='Someone completed your quiz',
            related_quiz=self.quiz
        )
        self.assertEqual(notification.recipient, self.user)
        self.assertFalse(notification.is_read)

    def test_notification_str_method(self):
        """Test the Notification string representation."""
        notification = Notification.objects.create(
            recipient=self.user,
            message='Test notification message'
        )
        self.assertIn('testuser', str(notification))

    def test_notification_default_type(self):
        """Test that default notification type is 'system'."""
        notification = Notification.objects.create(
            recipient=self.user,
            message='Test notification'
        )
        self.assertEqual(notification.notification_type, 'system')


class HomeViewTest(TestCase):
    """Test cases for the home view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

    def test_home_view_status_code(self):
        """Test that home view returns 200."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_template(self):
        """Test that home view uses correct template."""
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'index.html')

    def test_home_view_shows_featured_quizzes(self):
        """Test that home view shows featured quizzes."""
        quiz = Quiz.objects.create(title='Featured Quiz', is_featured=True)
        response = self.client.get(reverse('home'))
        self.assertIn(quiz, response.context['featured_quizzes'])


class QuizDetailViewTest(TestCase):
    """Test cases for the quiz detail view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.quiz = Quiz.objects.create(title='Test Quiz')
        self.question = Question.objects.create(
            quiz=self.quiz,
            text='Test Question',
            option_a='A',
            option_b='B',
            option_c='C',
            option_d='D',
            correct_answer='A',
            order=1
        )

    def test_quiz_detail_view_status_code(self):
        """Test that quiz detail view returns 200."""
        response = self.client.get(
            reverse('quizzes:detail', kwargs={'slug': self.quiz.slug})
        )
        self.assertEqual(response.status_code, 200)

    def test_quiz_detail_view_template(self):
        """Test that quiz detail view uses correct template."""
        response = self.client.get(
            reverse('quizzes:detail', kwargs={'slug': self.quiz.slug})
        )
        self.assertTemplateUsed(response, 'quizzes/quiz_detail.html')

    def test_quiz_detail_view_context(self):
        """Test that quiz detail view has correct context."""
        response = self.client.get(
            reverse('quizzes:detail', kwargs={'slug': self.quiz.slug})
        )
        self.assertEqual(response.context['quiz'], self.quiz)
        self.assertEqual(len(response.context['questions']), 1)

    def test_quiz_detail_404_for_invalid_slug(self):
        """Test that 404 is returned for invalid slug."""
        response = self.client.get(
            reverse('quizzes:detail', kwargs={'slug': 'nonexistent-quiz'})
        )
        self.assertEqual(response.status_code, 404)


class QuizSubmitViewTest(TestCase):
    """Test cases for the quiz submit view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.quiz = Quiz.objects.create(title='Test Quiz')
        self.question = Question.objects.create(
            quiz=self.quiz,
            text='Test Question',
            option_a='Correct',
            option_b='Wrong',
            option_c='Wrong',
            option_d='Wrong',
            correct_answer='A',
            order=1
        )

    def test_quiz_submit_redirects_on_get(self):
        """Test that GET request redirects to quiz detail."""
        response = self.client.get(
            reverse('quizzes:submit', kwargs={'slug': self.quiz.slug})
        )
        self.assertEqual(response.status_code, 302)

    def test_quiz_submit_post_shows_results(self):
        """Test that POST shows quiz results."""
        response = self.client.post(
            reverse('quizzes:submit', kwargs={'slug': self.quiz.slug}),
            {f'question_{self.question.id}': 'A'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quizzes/quiz_results.html')

    def test_quiz_submit_calculates_score(self):
        """Test that submit calculates score correctly."""
        response = self.client.post(
            reverse('quizzes:submit', kwargs={'slug': self.quiz.slug}),
            {f'question_{self.question.id}': 'A'}
        )
        self.assertEqual(response.context['correct_count'], 1)
        self.assertEqual(response.context['score_percentage'], 100)

    def test_quiz_submit_creates_attempt_for_logged_user(self):
        """Test that quiz attempt is created for logged in user."""
        self.client.login(username='testuser', password='testpass123')
        self.client.post(
            reverse('quizzes:submit', kwargs={'slug': self.quiz.slug}),
            {f'question_{self.question.id}': 'A'}
        )
        attempt = QuizAttempt.objects.filter(
            user=self.user, quiz=self.quiz).first()
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.score, 1)

    def test_quiz_submit_creates_notification_for_creator(self):
        """Test that notification is created for quiz creator."""
        creator = User.objects.create_user(
            username='creator',
            password='testpass123'
        )
        self.quiz.creator = creator
        self.quiz.save()

        self.client.login(username='testuser', password='testpass123')
        self.client.post(
            reverse('quizzes:submit', kwargs={'slug': self.quiz.slug}),
            {f'question_{self.question.id}': 'A'}
        )

        notification = Notification.objects.filter(
            recipient=creator,
            notification_type='quiz_completed'
        ).first()
        self.assertIsNotNone(notification)


class QuizCreateViewTest(TestCase):
    """Test cases for the quiz create view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_quiz_create_requires_login(self):
        """Test that quiz create requires authentication."""
        response = self.client.get(reverse('quizzes:create'))
        self.assertEqual(response.status_code, 302)

    def test_quiz_create_get(self):
        """Test GET request to quiz create."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('quizzes:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quizzes/quiz_create.html')


class TemplateTagsTest(TestCase):
    """Test cases for custom template tags and filters."""

    def test_quiz_card_displays_correctly(self):
        """Test that quiz cards display correctly on home page."""
        Quiz.objects.create(
            title='Test Quiz',
            description='A test quiz description',
            is_featured=True
        )
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Test Quiz')

    def test_questions_count_displayed(self):
        """Test that question count is displayed."""
        quiz = Quiz.objects.create(title='Test Quiz', is_featured=True)
        Question.objects.create(
            quiz=quiz, text='Q1', option_a='A', option_b='B',
            option_c='C', option_d='D', correct_answer='A', order=1
        )
        response = self.client.get(reverse('home'))
        self.assertContains(response, '1')
