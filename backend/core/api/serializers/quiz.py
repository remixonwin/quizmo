from rest_framework import serializers
from backend.core.models import Quiz, Question, Choice

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'points', 'choices', 'quiz']

    def validate_choices(self, value):
        """
        Check that at least two choices are provided
        """
        if len(value) < 2:
            raise serializers.ValidationError("At least two choices are required")
        return value

    def validate_points(self, value):
        """
        Check that points are non-negative
        """
        if value < 0:
            raise serializers.ValidationError("Points must be non-negative")
        return value

    def create(self, validated_data):
        choices_data = validated_data.pop('choices', [])
        if not choices_data:
            raise serializers.ValidationError({"choices": "At least two choices are required"})
            
        question = Question.objects.create(**validated_data)
        
        for choice_data in choices_data:
            Choice.objects.create(question=question, **choice_data)
        return question

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'questions']

    def validate_questions(self, value):
        """
        Check that at least one question is provided and each question has valid choices
        """
        if not value:
            raise serializers.ValidationError("At least one question is required")
        
        for question in value:
            choices = question.get('choices', [])
            if len(choices) < 2:
                raise serializers.ValidationError("Each question must have at least two choices")
            if not any(choice.get('is_correct', False) for choice in choices):
                raise serializers.ValidationError("Each question must have at least one correct answer")
        return value

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        quiz = Quiz.objects.create(**validated_data)
        
        for question_data in questions_data:
            choices_data = question_data.pop('choices', [])
            question = Question.objects.create(quiz=quiz, **question_data)
            
            for choice_data in choices_data:
                Choice.objects.create(question=question, **choice_data)
        return quiz

    def update(self, instance, validated_data):
        if 'questions' in validated_data:
            questions_data = validated_data.pop('questions')
            instance.questions.all().delete()  # Remove existing questions
            
            for question_data in questions_data:
                choices_data = question_data.pop('choices')
                question = Question.objects.create(quiz=instance, **question_data)
                
                for choice_data in choices_data:
                    Choice.objects.create(question=question, **choice_data)

        return super().update(instance, validated_data)