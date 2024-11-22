"""
UI tests for quiz creation functionality.
"""
from django.contrib.auth import get_user_model
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base import BaseUITest

class QuizCreationTest(BaseUITest):
    """Test the quiz creation process from a user's perspective."""

    def setUp(self):
        """Set up test data."""
        super().setUp()  # Call parent's setUp to initialize browser
        
        User = get_user_model()
        self.username = "testuser"
        self.password = "testpass123"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="test@example.com"
        )

    def test_create_quiz(self):
        """Test creating a new quiz."""
        # Log in
        self.login(self.username, self.password)

        # Navigate to quiz creation page
        self.browser.get(f"{self.live_server_url}/quizzes/create/")

        # Fill in quiz details
        title_input = self.wait_for_element(By.ID, "id_title")
        title_input.send_keys("Test Quiz")

        description_input = self.wait_for_element(By.ID, "id_description")
        description_input.send_keys("This is a test quiz created by UI automation")

        time_limit_input = self.wait_for_element(By.ID, "id_time_limit")
        time_limit_input.send_keys("30")

        # Add a question
        add_question_btn = self.wait_for_element(By.CLASS_NAME, "add-question-btn")
        add_question_btn.click()

        # Fill in question details
        question_text = self.wait_for_element(By.NAME, "questions-0-text")
        question_text.send_keys("What is the capital of France?")

        points_input = self.wait_for_element(By.NAME, "questions-0-points")
        points_input.send_keys("1")

        # Add choices
        choices = [
            ("Paris", True),
            ("London", False),
            ("Berlin", False)
        ]

        for i, (choice_text, is_correct) in enumerate(choices):
            choice_input = self.wait_for_element(
                By.NAME,
                f"questions-0-choices-{i}-text"
            )
            choice_input.send_keys(choice_text)

            if is_correct:
                correct_choice = self.wait_for_element(
                    By.NAME,
                    f"questions-0-choices-{i}-is_correct"
                )
                correct_choice.click()

        # Submit the form
        submit_button = self.wait_for_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Verify we're redirected to the quiz detail page
        self.wait_for_element(By.CLASS_NAME, "quiz-detail")
        self.assertIn("Test Quiz", self.browser.title)

    def test_quiz_validation(self):
        """Test form validation for quiz creation."""
        # Log in
        self.login(self.username, self.password)

        # Navigate to quiz creation page
        self.browser.get(f"{self.live_server_url}/quizzes/create/")

        # Try to submit empty form
        submit_button = self.wait_for_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Check for error messages
        error_messages = self.browser.find_elements(By.CLASS_NAME, "error-message")
        self.assertTrue(len(error_messages) > 0)

        # Try to create quiz without choices
        title_input = self.wait_for_element(By.ID, "id_title")
        title_input.send_keys("Invalid Quiz")

        add_question_btn = self.wait_for_element(By.CLASS_NAME, "add-question-btn")
        add_question_btn.click()

        question_text = self.wait_for_element(By.NAME, "questions-0-text")
        question_text.send_keys("A question without choices")

        submit_button.click()

        # Check for error about missing choices
        error_messages = self.browser.find_elements(By.CLASS_NAME, "error-message")
        self.assertTrue(any("choices" in msg.text.lower() for msg in error_messages))
