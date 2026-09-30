#!/usr/bin/env node
// Read-only local UI smoke inspection. Uses only an already cached Playwright install.
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { createRequire } = require('node:module');

function argsFrom(argv) {
  const out = { url: null, screenshots: false };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--url') out.url = argv[++i];
    else if (argv[i] === '--screenshots') out.screenshots = true;
    else throw new Error(`Unknown argument: ${argv[i]}`);
  }
  if (!out.url) throw new Error('Usage: inspect_local_app.cjs --url http://127.0.0.1:PORT/ [--screenshots]');
  const parsed = new URL(out.url);
  if (parsed.protocol !== 'http:' || !['localhost', '127.0.0.1', '::1'].includes(parsed.hostname)) {
    throw new Error('--url must be an http:// loopback URL');
  }
  return out;
}

function cachedPlaywright() {
  const cache = path.join(os.homedir(), '.npm', '_npx');
  if (!fs.existsSync(cache)) throw new Error('No existing npm Playwright cache; no package was installed.');
  const manifests = [];
  for (const entry of fs.readdirSync(cache)) {
    const manifest = path.join(cache, entry, 'node_modules', '@playwright', 'mcp', 'package.json');
    if (fs.existsSync(manifest)) manifests.push(manifest);
  }
  manifests.sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
  for (const manifest of manifests) {
    try {
      const load = createRequire(manifest);
      const playwright = load('playwright');
      const executable = playwright.chromium.executablePath();
      fs.accessSync(executable, fs.constants.X_OK);
      return { playwright, executable };
    } catch (_) {
      // Try another existing MCP cache entry; do not download or install anything.
    }
  }
  throw new Error('No cached @playwright/mcp package has a usable Chromium binary.');
}

async function inspect(page, url, width, height, screenshotPath) {
  const consoleErrors = [];
  const pageErrors = [];
  const failedRequests = [];
  const badResponses = [];
  const blockedExternal = [];
  page.on('console', message => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  page.on('pageerror', error => pageErrors.push(error.message));
  page.on('requestfailed', request => {
    failedRequests.push({ url: request.url(), reason: request.failure()?.errorText || 'unknown' });
  });
  page.on('response', response => {
    if (response.status() >= 400) badResponses.push({ status: response.status(), url: response.url() });
  });
  await page.route('**/*', route => {
    const requestUrl = new URL(route.request().url());
    if (['http:', 'https:'].includes(requestUrl.protocol) && ['localhost', '127.0.0.1', '::1'].includes(requestUrl.hostname)) {
      return route.continue();
    }
    blockedExternal.push(requestUrl.origin || requestUrl.protocol);
    return route.abort('blockedbyclient');
  });
  const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(500);
  const dom = await page.evaluate(() => ({
    title: document.title,
    headings: [...document.querySelectorAll('h1, h2')].slice(0, 12).map(node => node.innerText.trim()),
    mainLandmarks: document.querySelectorAll('main').length,
    visibleTextLength: document.body.innerText.length,
    viewportWidth: innerWidth,
    documentWidth: document.documentElement.scrollWidth,
    horizontalOverflow: document.documentElement.scrollWidth > innerWidth,
  }));
  if (screenshotPath) await page.screenshot({ path: screenshotPath, fullPage: true });
  return {
    viewport: `${width}x${height}`,
    httpStatus: response?.status() ?? null,
    dom,
    consoleErrors,
    pageErrors,
    failedRequests,
    badResponses,
    blockedExternal: [...new Set(blockedExternal)],
    screenshot: screenshotPath || null,
  };
}

async function main() {
  const args = argsFrom(process.argv.slice(2));
  const { playwright, executable } = cachedPlaywright();
  let screenshotDir = null;
  let browser = null;
  const results = [];
  try {
    browser = await playwright.chromium.launch({ headless: true, executablePath: executable });
    screenshotDir = args.screenshots ? fs.mkdtempSync(path.join(os.tmpdir(), 'webapp-qa-')) : null;
    for (const [name, width, height] of [['desktop', 1440, 900], ['mobile', 390, 844]]) {
      const context = await browser.newContext({ viewport: { width, height } });
      const page = await context.newPage();
      const screenshot = screenshotDir ? path.join(screenshotDir, `${name}.png`) : null;
      results.push({ name, ...(await inspect(page, args.url, width, height, screenshot)) });
      await context.close();
    }
  } finally {
    if (browser) await browser.close();
  }
  console.log(JSON.stringify({ browser: 'existing cached Playwright/Chromium', screenshotDir, results }, null, 2));
}

main().catch(error => {
  console.error(error.message);
  process.exitCode = 1;
});
