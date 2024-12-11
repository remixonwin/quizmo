import puppeteer, { Browser, Page } from 'puppeteer';

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

  it('should display the welcome message', async () => {
    await page.goto('http://localhost:3030');
    await page.waitForSelector('h1');
    const welcomeMessage = await page.$eval('h1', el => el.textContent);
    expect(welcomeMessage).toBe('Welcome to the Frontend');
  });

  it('should fetch and display the message from IPFS', async () => {
    await page.goto('http://localhost:3030');
    await page.waitForSelector('#message');
    const message = await page.$eval('#message', el => el.textContent);
    expect(message).toBe('Hello, IPFS!');
  });
});