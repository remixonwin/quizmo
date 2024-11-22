"""
UI tests for quiz-taking functionality.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base import BaseUITest
from quiz.models import Quiz, Question, Choice

class QuizTakingTest(BaseUITest):
    """Test the quiz-taking experience from a user's perspective."""

    def setUp(self):
        """Set up test data."""
        super().setUp()  # Call parent's setUp to initialize browser
        
        # Create test user
        User = get_user_model()
        self.username = "testuser"
        self.password = "testpass123"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="test@example.com",
            is_active=True  # Ensure user is active
        )

        # Create a test quiz
        self.quiz = Quiz.objects.create(
            title="Test Quiz",
            description="A test quiz for UI testing",
            created_by=self.user,
            time_limit=30
        )

        # Create a test question
        self.question = Question.objects.create(
            quiz=self.quiz,
            text="What is the capital of France?",
            points=1
        )

        # Create choices
        Choice.objects.create(question=self.question, text="London", is_correct=False)
        Choice.objects.create(question=self.question, text="Paris", is_correct=True)
        Choice.objects.create(question=self.question, text="Berlin", is_correct=False)

    def test_take_quiz(self):
        """Test taking a quiz from start to finish."""
        # Log in
        self.login(self.username, self.password)

        # Navigate to quiz list
        quiz_list_url = reverse('quiz:quiz_list')
        self.browser.get(f"{self.live_server_url}{quiz_list_url}")
        
        # Find and click on the test quiz
        quiz_link = self.wait_for_element(By.LINK_TEXT, "Test Quiz")
        quiz_link.click()

        # Wait for quiz page to load and click start
        start_button = self.wait_for_element(By.CLASS_NAME, "start-quiz-btn")
        start_button.click()

        # Answer the question
        choice_radio = self.wait_for_element(
            By.CSS_SELECTOR,
            'input[type="radio"][value="Paris"]'
        )
        choice_radio.click()

        # Submit answer
        submit_button = self.wait_for_element(By.CLASS_NAME, "submit-answer-btn")
        submit_button.click()

        # Verify we're on the results page
        results_heading = self.wait_for_element(By.CLASS_NAME, "quiz-results")
        self.assertIn("Quiz Results", results_heading.text)

        # Verify score
        score_element = self.wait_for_element(By.CLASS_NAME, "quiz-score")
        self.assertIn("1", score_element.text)  # We should have gotten 1 point

    def test_quiz_timeout(self):
        """Test that quiz times out appropriately."""
        # Log in
        self.login(self.username, self.password)

        # Set a very short time limit
        self.quiz.time_limit = 1  # 1 minute
        self.quiz.save()

        # Start the quiz
        quiz_url = reverse('quiz:quiz_detail', args=[self.quiz.id])
        self.browser.get(f"{self.live_server_url}{quiz_url}")
        start_button = self.wait_for_element(By.CLASS_NAME, "start-quiz-btn")
        start_button.click()

        # Wait for timeout
        timeout_message = self.wait_for_element(By.CLASS_NAME, "timeout-message")
        self.assertIn("Time's up!", timeout_message.text)
