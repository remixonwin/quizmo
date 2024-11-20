from django.contrib import admin
from .models import Quiz, Question, Choice

# Register your models here.

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    fields = ('text', 'is_correct', 'explanation')

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('text', 'order', 'explanation')
    show_change_link = True

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'question_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    inlines = [QuestionInline]
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'order', 'has_correct_answer')
    list_filter = ('quiz', 'order')
    search_fields = ('text', 'explanation')
    ordering = ('quiz', 'order')
    inlines = [ChoiceInline]
    
    def has_correct_answer(self, obj):
        return obj.choices.filter(is_correct=True).exists()
    has_correct_answer.boolean = True
    has_correct_answer.short_description = 'Has Correct Answer'

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('is_correct', 'question__quiz')
    search_fields = ('text', 'explanation')
    ordering = ('question', 'id')
