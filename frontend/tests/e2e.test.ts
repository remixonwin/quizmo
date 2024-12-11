import puppeteer, { Browser, Page } from 'puppeteer';

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3030';
const MAX_RETRIES = 3;
const RETRY_DELAY = 2000;

describe('E2E Testing', () => {
  let browser: Browser;
  let page: Page;

  beforeAll(async () => {
    browser = await puppeteer.launch({ headless: true });
    page = await browser.newPage();
  });

  afterAll(async () => {
    await browser.close();
  });

  const retryOperation = async (operation: () => Promise<void>) => {
    for (let i = 0; i < MAX_RETRIES; i++) {
      try {
        await operation();
        return;
      } catch (error) {
        if (i === MAX_RETRIES - 1) throw error;
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
      }
    }
  };

  it('should display the welcome message', async () => {
    await retryOperation(async () => {
      await page.goto(FRONTEND_URL);
      await page.waitForSelector('h1', { timeout: 5000 });
      const welcomeMessage = await page.$eval('h1', el => el.textContent);
      expect(welcomeMessage).toBe('Welcome to the Frontend');
    });
  });

  it('should fetch and display the message from IPFS', async () => {
    await retryOperation(async () => {
      await page.goto(FRONTEND_URL);
      await page.waitForSelector('#message', { timeout: 5000 });
      const message = await page.$eval('#message', el => el.textContent);
      expect(message).toBe('Hello, IPFS!');
    });
  });
});