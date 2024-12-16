import unittest
from playwright.sync_api import sync_playwright

class TestQuizFlow(unittest.TestCase):
    
    def setUp(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()
        self.page.goto("http://localhost:8501")
    
    def tearDown(self):
        self.browser.close()
        self.playwright.stop()
    
    def test_quiz_creation_and_take(self):
        # Create a new quiz
        self.page.click("text=Create Quiz")
        self.page.fill("input[name='title']", "End-to-End Test Quiz")
        self.page.fill("textarea[name='description']", "Testing quiz creation and taking.")
        self.page.click("text=Add Question")
        self.page.fill("textarea[name='q0_text']", "What is the capital of France?")
        self.page.fill("input[name='q0_choice_0']", "Paris")
        self.page.fill("input[name='q0_choice_1']", "London")
        self.page.click("text=Submit")
        self.page.wait_for_selector("text=Quiz created successfully")
        
        # Take the quiz
        self.page.click("text=Start Quiz")
        self.page.fill("textarea[name='q0_text']", "Paris")
        self.page.click("text=Submit Answers")
        self.page.wait_for_selector("text=Your score:")

if __name__ == '__main__':
    unittest.main()
