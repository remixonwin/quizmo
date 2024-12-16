
from rest_framework import viewsets
from backend.core.models import Quiz
from ..serializers.quiz import QuizSerializer
from rest_framework.permissions import IsAuthenticated

class QuizViewSet(viewsets.ModelViewSet):
    """ViewSet for managing quizzes"""
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]