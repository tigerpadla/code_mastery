"""
Tests for the accounts app.
Tests cover models, views, and templates.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile
from quizzes.models import Quiz, QuizAttempt, Notification


class ProfileModelTest(TestCase):
    """Test cases for the Profile model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_profile_created_on_user_creation(self):
        """Test that a Profile is automatically created when a User is created."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, Profile)

    def test_profile_str_method(self):
        """Test the Profile string representation."""
        expected = f"{self.user.username}'s profile"
        self.assertEqual(str(self.user.profile), expected)

    def test_profile_default_avatar(self):
        """Test that the default avatar is 'male'."""
        self.assertEqual(self.user.profile.avatar, 'male')

    def test_get_avatar_url_male(self):
        """Test get_avatar_url returns correct URL for male avatar."""
        self.user.profile.avatar = 'male'
        self.user.profile.save()
        self.assertEqual(
            self.user.profile.get_avatar_url(),
            '/static/images/user-male-icon.png'
        )

    def test_get_avatar_url_female(self):
        """Test get_avatar_url returns correct URL for female avatar."""
        self.user.profile.avatar = 'female'
        self.user.profile.save()
        self.assertEqual(
            self.user.profile.get_avatar_url(),
            '/static/images/user-female-icon.png'
        )

    def test_profile_bio_blank_by_default(self):
        """Test that bio is blank by default."""
        self.assertEqual(self.user.profile.bio, '')

    def test_profile_saved_quizzes_empty_by_default(self):
        """Test that saved_quizzes is empty by default."""
        self.assertEqual(self.user.profile.saved_quizzes.count(), 0)

    def test_profile_can_save_quiz(self):
        """Test that a profile can save a quiz."""
        quiz = Quiz.objects.create(
            title='Test Quiz',
            creator=self.user
        )
        self.user.profile.saved_quizzes.add(quiz)
        self.assertIn(quiz, self.user.profile.saved_quizzes.all())


class ProfileViewTest(TestCase):
    """Test cases for profile views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )

    def test_own_profile_view_authenticated(self):
        """Test viewing own profile when authenticated."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/profile.html')
        self.assertTrue(response.context['is_own_profile'])

    def test_own_profile_view_unauthenticated_redirects(self):
        """Test that unauthenticated users are redirected from own profile."""
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)

    def test_public_profile_view(self):
        """Test viewing another user's public profile."""
        response = self.client.get(
            reverse('accounts:profile_user', kwargs={'username': 'testuser'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/profile.html')

    def test_public_profile_hides_saved_quizzes(self):
        """Test that saved quizzes are hidden on public profiles."""
        response = self.client.get(
            reverse('accounts:profile_user', kwargs={'username': 'testuser'})
        )
        self.assertEqual(len(response.context['saved_quizzes']), 0)

    def test_profile_404_for_nonexistent_user(self):
        """Test that 404 is returned for nonexistent username."""
        response = self.client.get(
            reverse('accounts:profile_user', kwargs={'username': 'nonexistent'})
        )
        self.assertEqual(response.status_code, 404)


class ProfileEditViewTest(TestCase):
    """Test cases for profile edit view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_profile_edit_requires_login(self):
        """Test that profile edit requires authentication."""
        response = self.client.get(reverse('accounts:profile_edit'))
        self.assertEqual(response.status_code, 302)

    def test_profile_edit_get(self):
        """Test GET request to profile edit."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:profile_edit'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/profile_edit.html')

    def test_profile_edit_post_updates_bio(self):
        """Test that POST updates the bio."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('accounts:profile_edit'), {
            'bio': 'This is my new bio',
            'avatar': 'male'
        })
        self.assertEqual(response.status_code, 302)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.bio, 'This is my new bio')

    def test_profile_edit_post_updates_avatar(self):
        """Test that POST updates the avatar choice."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('accounts:profile_edit'), {
            'bio': '',
            'avatar': 'female'
        })
        self.assertEqual(response.status_code, 302)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.avatar, 'female')


class SaveQuizViewTest(TestCase):
    """Test cases for save/unsave quiz functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.quiz_creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='testpass123'
        )
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            creator=self.quiz_creator
        )

    def test_save_quiz_requires_login(self):
        """Test that saving a quiz requires authentication."""
        response = self.client.get(
            reverse('accounts:save_quiz', kwargs={'quiz_id': self.quiz.id})
        )
        self.assertEqual(response.status_code, 302)

    def test_save_quiz_adds_to_saved(self):
        """Test that saving a quiz adds it to saved quizzes."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('accounts:save_quiz', kwargs={'quiz_id': self.quiz.id})
        )
        self.assertIn(self.quiz, self.user.profile.saved_quizzes.all())

    def test_unsave_quiz_removes_from_saved(self):
        """Test that unsaving a quiz removes it from saved quizzes."""
        self.client.login(username='testuser', password='testpass123')
        self.user.profile.saved_quizzes.add(self.quiz)
        response = self.client.get(
            reverse('accounts:save_quiz', kwargs={'quiz_id': self.quiz.id})
        )
        self.assertNotIn(self.quiz, self.user.profile.saved_quizzes.all())

    def test_save_quiz_creates_notification(self):
        """Test that saving creates a notification for quiz creator."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('accounts:save_quiz', kwargs={'quiz_id': self.quiz.id})
        )
        notification = Notification.objects.filter(
            recipient=self.quiz_creator,
            notification_type='quiz_saved'
        ).first()
        self.assertIsNotNone(notification)


class QuizHistoryViewTest(TestCase):
    """Test cases for quiz history view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            creator=self.user
        )

    def test_quiz_history_requires_login(self):
        """Test that quiz history requires authentication."""
        response = self.client.get(reverse('accounts:quiz_history'))
        self.assertEqual(response.status_code, 302)

    def test_quiz_history_shows_attempts(self):
        """Test that quiz history shows user's attempts."""
        self.client.login(username='testuser', password='testpass123')
        QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            score=8,
            total_questions=10
        )
        response = self.client.get(reverse('accounts:quiz_history'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['attempts']), 1)


class MyQuizzesViewTest(TestCase):
    """Test cases for my quizzes view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_my_quizzes_requires_login(self):
        """Test that my quizzes page requires authentication."""
        response = self.client.get(reverse('accounts:my_quizzes'))
        self.assertEqual(response.status_code, 302)

    def test_my_quizzes_shows_created_quizzes(self):
        """Test that my quizzes shows user's created quizzes."""
        self.client.login(username='testuser', password='testpass123')
        Quiz.objects.create(title='My Quiz 1', creator=self.user)
        Quiz.objects.create(title='My Quiz 2', creator=self.user)
        response = self.client.get(reverse('accounts:my_quizzes'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), 2)


class SavedQuizzesViewTest(TestCase):
    """Test cases for saved quizzes view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.quiz = Quiz.objects.create(title='Test Quiz')

    def test_saved_quizzes_requires_login(self):
        """Test that saved quizzes page requires authentication."""
        response = self.client.get(reverse('accounts:saved_quizzes'))
        self.assertEqual(response.status_code, 302)

    def test_saved_quizzes_shows_saved_quizzes(self):
        """Test that saved quizzes shows user's saved quizzes."""
        self.client.login(username='testuser', password='testpass123')
        self.user.profile.saved_quizzes.add(self.quiz)
        response = self.client.get(reverse('accounts:saved_quizzes'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), 1)


class NotificationsViewTest(TestCase):
    """Test cases for notifications view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_notifications_requires_login(self):
        """Test that notifications page requires authentication."""
        response = self.client.get(reverse('accounts:notifications'))
        self.assertEqual(response.status_code, 302)

    def test_notifications_shows_user_notifications(self):
        """Test that notifications shows user's notifications."""
        self.client.login(username='testuser', password='testpass123')
        Notification.objects.create(
            recipient=self.user,
            message='Test notification'
        )
        response = self.client.get(reverse('accounts:notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['notifications']), 1)

    def test_mark_all_notifications_read(self):
        """Test marking all notifications as read."""
        self.client.login(username='testuser', password='testpass123')
        Notification.objects.create(
            recipient=self.user,
            message='Test notification',
            is_read=False
        )
        response = self.client.post(reverse('accounts:notifications_mark_all_read'))
        notification = Notification.objects.first()
        self.assertTrue(notification.is_read)

