import unittest
from playwright.sync_api import sync_playwright

class TestQuizFlow(unittest.TestCase):
    
    def setUp(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.goto("http://localhost:8501")

        # Wait for initial page load
        self.page.wait_for_load_state('networkidle')
        self.page.wait_for_selector("text=Login", timeout=15000)

        # Login first
        self.login()
    
    def login(self):
        self.page.fill("input[placeholder='Username']", "testuser")
        self.page.fill("input[placeholder='Password']", "testpass123")
        self.page.click("text=Login")
        self.page.wait_for_selector("text=Create Quiz", timeout=15000)
    
    def tearDown(self):
        self.browser.close()
        self.playwright.stop()
    
    def test_quiz_creation_and_take(self):
        # Ensure page is loaded
        self.page.wait_for_load_state('networkidle')
        self.page.wait_for_selector("text=Create Quiz", state="visible", timeout=30000)
        
        # Create quiz
        self.page.click("text=Create Quiz")
        self.page.wait_for_selector("input[name='title']", timeout=5000)
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
