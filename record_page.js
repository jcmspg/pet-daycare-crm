const { chromium } = require('playwright');

async function smoothScroll(page, total = 2200, step = 6, delay = 16) {
  for (let scrolled = 0; scrolled < total; scrolled += step) {
    await page.evaluate(([s]) => window.scrollBy({ top: s, behavior: 'smooth' }), [step]);
    await page.waitForTimeout(delay);
  }
}

const targets = {
  feed: {
    url: 'http://localhost:8000/staff/feed/',
    creds: { user: 'staff1_manager@somemail.com', pass: 'SecurePass123!' },
    total: 2800
  },
  staff: {
    url: 'http://localhost:8000/staff/dashboard/',
    creds: { user: 'staff1_manager@somemail.com', pass: 'SecurePass123!' },
    total: 1800
  },
  tutor: {
    url: 'http://localhost:8000/tutor/dashboard/',
    creds: { user: 'tutor1@somemail.com', pass: 'SecurePass123!' },
    total: 1800
  }
};

(async () => {
  const key = process.argv[2];
  if (!targets[key]) {
    console.error('Usage: node record_page.js feed|staff|tutor');
    process.exit(1);
  }
  const target = targets[key];

  const browser = await chromium.launch({ headless: true });
  
  // First, login without recording
  const loginContext = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const loginPage = await loginContext.newPage();
  
  await loginPage.goto('http://localhost:8000/accounts/login/');
  await loginPage.fill('input[name="login"]', target.creds.user);
  await loginPage.fill('input[name="password"]', target.creds.pass);
  await loginPage.click('button[type="submit"]');
  
  // Wait for login to complete by checking URL change
  try {
    await loginPage.waitForURL('**/**', { timeout: 5000 });
  } catch (err) {
    // ignore
  }
  await loginPage.waitForTimeout(2000);
  
  // Get cookies and close login context
  const cookies = await loginContext.cookies();
  await loginContext.close();

  // Now create recording context with cookies already set
  const recordContext = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    recordVideo: { dir: 'videos', size: { width: 1280, height: 900 } },
    extraHTTPHeaders: {}
  });
  
  // Add cookies
  await recordContext.addCookies(cookies);

  const recordPage = await recordContext.newPage();
  
  // Load target page (already authenticated)
  await recordPage.goto(target.url);
  
  // Wait for content to load
  await recordPage.waitForTimeout(2000);
  
  // Now scroll and record
  await smoothScroll(recordPage, target.total, 6, 16);
  await recordPage.waitForTimeout(500);

  await recordContext.close();
  await browser.close();
  console.log(`Saved video for ${key}`);
})();
