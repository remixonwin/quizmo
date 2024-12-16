from .auth import User
from .quiz import Quiz, Question, Choice

default_app_config = 'backend.core.apps.CoreConfig'

__all__ = ['User', 'Quiz', 'Question', 'Choice']