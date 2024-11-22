"""
Base test class for authentication tests.
"""
from django.test import TestCase
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from quiz.models import Quiz

class AuthTestCase(TestCase):
    """Base test case for authentication tests."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test users and permissions."""
        # Create test user
        cls.test_user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

        # Create test admin
        cls.test_admin = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@example.com'
        )

        # Create test staff
        cls.test_staff = User.objects.create_user(
            username='staff',
            password='staffpass123',
            email='staff@example.com',
            is_staff=True
        )
        
        # Set up common groups
        cls.setup_groups()
        
        # Set up common permissions
        cls.setup_permissions()
    
    @classmethod
    def setup_groups(cls):
        """Set up common test groups."""
        cls.teacher_group = Group.objects.create(name='Teachers')
        cls.student_group = Group.objects.create(name='Students')
        cls.moderator_group = Group.objects.create(name='Moderators')
    
    @classmethod
    def setup_permissions(cls):
        """Set up common test permissions."""
        # Get content type for Quiz model
        quiz_content_type = ContentType.objects.get_for_model(Quiz)
        
        # Create quiz permissions
        cls.can_create_quiz = Permission.objects.create(
            codename='can_create_quiz',
            name='Can create quiz',
            content_type=quiz_content_type,
        )
        cls.can_edit_quiz = Permission.objects.create(
            codename='can_edit_quiz',
            name='Can edit quiz',
            content_type=quiz_content_type,
        )
        cls.can_delete_quiz = Permission.objects.create(
            codename='can_delete_quiz',
            name='Can delete quiz',
            content_type=quiz_content_type,
        )
        
        # Assign permissions to groups
        cls.teacher_group.permissions.add(
            cls.can_create_quiz,
            cls.can_edit_quiz,
            cls.can_delete_quiz
        )
        cls.moderator_group.permissions.add(
            cls.can_edit_quiz
        )
