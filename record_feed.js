const { chromium } = require('playwright');

async function smoothScroll(page, total = 2800, step = 6, delay = 16) {
  // Smooth, near-60fps glide
  for (let scrolled = 0; scrolled < total; scrolled += step) {
    await page.evaluate(([s]) => window.scrollBy({ top: s, behavior: 'smooth' }), [step]);
    await page.waitForTimeout(delay);
  }
}

async function record(url) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    recordVideo: { dir: 'videos', size: { width: 1280, height: 900 } }
  });
  const page = await context.newPage();

  // Login (manager)
  await page.goto('http://localhost:8000/accounts/login/');
  await page.fill('input[name="login"]', 'staff1_manager@somemail.com');
  await page.fill('input[name="password"]', 'SecurePass123!');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1200);

  // Navigate to target and glide
  await page.goto(url);
  await page.waitForTimeout(1200);
  await smoothScroll(page, 2800, 6, 16);
  await page.waitForTimeout(800);

  await context.close();
  await browser.close();
}

// Usage: node record_feed.js feed|dashboard
const target = process.argv[2];
if (!target) {
  console.error('Usage: node record_feed.js feed|dashboard');
  process.exit(1);
}

const urlMap = {
  feed: 'http://localhost:8000/staff/feed/',
  dashboard: 'http://localhost:8000/staff/dashboard/'
};

if (!urlMap[target]) {
  console.error('Unknown target. Use feed or dashboard.');
  process.exit(1);
}

record(urlMap[target]).catch(err => {
  console.error(err);
  process.exit(1);
});
