import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';

// Focused 02-01 evidence: open the staged Studio, load the real production
// pistol GLB, and capture the perspectives used in the visual review.
const studio = process.env.STUDIO_URL || 'http://127.0.0.1:8811';
const out = process.env.CAPTURE_DIR || '/tmp/studio-hybrid';
const tag = process.env.CAPTURE_TAG || 'after';
await mkdir(out, { recursive: true });

const browser = await chromium.launch({
  headless: true,
  args: ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
});
const page = await browser.newPage({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1 });
const errors = [];
const external = [];
const origin = new URL(studio).origin;
page.on('pageerror', (error) => errors.push(error.message));
page.on('request', (request) => {
  const url = new URL(request.url());
  if (['http:', 'https:'].includes(url.protocol) && url.origin !== origin) external.push(request.url());
});
await page.route('**/*', (route) => {
  const url = new URL(route.request().url());
  return ['http:', 'https:'].includes(url.protocol) && url.origin !== origin
    ? route.abort()
    : route.continue();
});

await page.goto(studio.endsWith('/') ? studio : studio + '/', { waitUntil: 'networkidle' });
await page.locator('#state[data-kind=ready]').waitFor({ timeout: 30000 });
await page.locator('#assets button', { hasText: 'weapon:pistol' }).first().click();
await page.locator('#variant').waitFor({ state: 'visible' });
await page.locator('#view').waitFor({ state: 'attached' });
await page.waitForFunction(() => document.querySelector('#state')?.dataset.kind === 'ready');
const variant = await page.locator('#variant').inputValue();
const resource = await page.locator('#viewport').getAttribute('data-resource');
const sha256 = await page.locator('#viewport').getAttribute('data-sha256');

async function shot(name, view, mode) {
  await page.selectOption('#view', view);
  if (mode) await page.selectOption('#inspection-mode', mode);
  await page.waitForTimeout(700);
  const bytes = await page.locator('#viewport').screenshot();
  const path = `${out}/${tag}-${name}.png`;
  const { writeFile } = await import('node:fs/promises');
  await writeFile(path, bytes);
  return { path, sha256: createHash('sha256').update(bytes).digest('hex'), bytes: bytes.length };
}

const captures = [];
captures.push(await shot('perspective', 'perspective'));
captures.push(await shot('right', 'right'));
captures.push(await shot('front', 'front'));
captures.push(await shot('top', 'top'));
captures.push(await shot('wireframe-right', 'right', 'wireframe'));
captures.push(await shot('solid-right', 'right', 'solid'));

const details = await page.locator('#details').innerText();
const metrics = await page.locator('#inspection-metrics').innerText().catch(() => '');
console.log(JSON.stringify({
  tag, studio, variant, resource, sha256, external, errors, captures,
  details: details.split('\n').slice(0, 24), metrics: metrics.split('\n').slice(0, 24),
}, null, 2));
await browser.close();
