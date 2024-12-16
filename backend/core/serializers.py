from rest_framework import serializers
from .models import Quiz, Question, Choice
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()  # Use get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

class RegisterSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ('id', 'username', 'email', 'password')

    def validate(self, attrs):
        # Validate password against username and email
        try:
            validate_password(attrs['password'], user=User(
                username=attrs.get('username'),
                email=attrs.get('email')
            ))
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
            
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, required=True)

    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text', 'points', 'image', 'choices']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'author', 'created_at', 'image', 'questions']
        read_only_fields = ['author']

    def validate(self, data):
        # Validate title and description
        if not data.get('title', '').strip():
            raise serializers.ValidationError({"title": "Title cannot be empty"})
        if not data.get('description', '').strip():
            raise serializers.ValidationError({"description": "Description cannot be empty"})
        
        # Validate questions
        questions = data.get('questions', [])
        if not questions:
            raise serializers.ValidationError({"questions": "At least one question is required"})
        
        return data

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        quiz = Quiz.objects.create(**validated_data)
        
        for question_data in questions_data:
            choices_data = question_data.pop('choices', [])
            question = Question.objects.create(quiz=quiz, **question_data)
            
            for choice_data in choices_data:
                Choice.objects.create(question=question, **choice_data)
        
        return quiz