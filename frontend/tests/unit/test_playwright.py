import unittest
from playwright.sync_api import sync_playwright

class TestPlaywrightQuizFlow(unittest.TestCase):
    
    def setUp(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()
        self.page.goto("http://localhost:8501")
    
    def tearDown(self):
        self.browser.close()
        self.playwright.stop()
    
    def test_create_quiz_flow(self):
        # Navigate to create quiz
        self.page.click("text=Create Quiz")
        # Fill in quiz details
        self.page.fill("input[name='title']", "Test Quiz")
        self.page.fill("textarea[name='description']", "A description for test quiz.")
        # Add a question
        self.page.click("text=Add Question")
        self.page.fill("textarea[name='q0_text']", "What is 2 + 2?")
        self.page.fill("input[name='q0_choice_0']", "3")
        self.page.fill("input[name='q0_choice_1']", "4")
        # Submit the quiz
        self.page.click("text=Submit")
        # Assert success message
        self.assertTrue(self.page.is_visible("text=Quiz created successfully"))

if __name__ == '__main__':
    unittest.main()
