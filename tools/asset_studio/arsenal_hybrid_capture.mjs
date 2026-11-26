import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';

// Focused 02-02 evidence: load each real production weapon GLB in the staged
// Studio and capture the review views. No synthetic geometry, no CDN.
const studio = process.env.STUDIO_URL || 'http://127.0.0.1:8821';
const out = process.env.CAPTURE_DIR || '/tmp/studio-arsenal';
const tag = process.env.CAPTURE_TAG || 'after';
const weapons = ['pistol', 'smg', 'rifle', 'shotgun', 'lmg', 'sniper', 'bolt_sniper', 'sentinela'];
const views = (process.env.CAPTURE_VIEWS || 'perspective,right').split(',');
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
  return ['http:', 'https:'].includes(url.protocol) && url.origin !== origin ? route.abort() : route.continue();
});

await page.goto(studio.endsWith('/') ? studio : studio + '/', { waitUntil: 'networkidle' });
await page.locator('#state[data-kind=ready]').waitFor({ timeout: 30000 });

const report = { tag, studio, external, errors, weapons: {} };
for (const weapon of weapons) {
  await page.locator(`#assets button[data-asset="weapon:${weapon}"]`).click();
  await page.waitForFunction(() => document.querySelector('#state')?.dataset.kind === 'ready');
  const variant = await page.locator('#variant').inputValue();
  const resource = await page.locator('#viewport').getAttribute('data-resource');
  const sha256 = await page.locator('#viewport').getAttribute('data-sha256');
  const metrics = (await page.locator('#inspection-metrics').innerText()).split('\n');
  const shots = [];
  for (const view of views) {
    await page.selectOption('#view', view);
    await page.waitForTimeout(600);
    const bytes = await page.locator('#viewport').screenshot();
    const path = `${out}/${tag}-${weapon}-${view}.png`;
    await writeFile(path, bytes);
    shots.push({ view, path, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex') });
  }
  report.weapons[weapon] = { variant, resource, sha256, metrics, shots };
}
await writeFile(`${out}/${tag}-report.json`, JSON.stringify(report, null, 2));
console.log(JSON.stringify({
  tag, external: external.length, errors,
  weapons: Object.fromEntries(Object.entries(report.weapons).map(([k, v]) => [k, { sha256: v.sha256, shots: v.shots.length }])),
}, null, 2));
await browser.close();
