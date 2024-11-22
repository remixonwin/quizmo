"""
User factory for creating test users.
"""
import factory
from django.contrib.auth.models import User

class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users."""
    
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    
    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        """Add user to groups if specified."""
        if not create:
            return

        if extracted:
            for group in extracted:
                self.groups.add(group)
                
    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        """Add permissions to user if specified."""
        if not create:
            return

        if extracted:
            for permission in extracted:
                self.user_permissions.add(permission)
