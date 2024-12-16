import unittest
from playwright.async_api import async_playwright

class TestPlaywrightQuizFlow(unittest.TestCase):
    
    async def setUp(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        await self.page.goto("http://localhost:8501")
    
    async def tearDown(self):
        await self.browser.close()
        await self.playwright.stop()
    
    async def test_create_quiz_flow(self):
        # Navigate to create quiz
        await self.page.click("text=Create Quiz")
        # Fill in quiz details
        await self.page.fill("input[name='title']", "Test Quiz")
        await self.page.fill("textarea[name='description']", "A description for test quiz.")
        # Add a question
        await self.page.click("text=Add Question")
        await self.page.fill("textarea[name='q0_text']", "What is 2 + 2?")
        await self.page.fill("input[name='q0_choice_0']", "3")
        await self.page.fill("input[name='q0_choice_1']", "4")
        # Submit the quiz
        await self.page.click("text=Submit")
        # Assert success message
        self.assertTrue(await self.page.is_visible("text=Quiz created successfully"))

if __name__ == '__main__':
    unittest.main()
