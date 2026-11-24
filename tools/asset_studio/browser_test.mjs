import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
const url=process.env.STUDIO_URL||'http://127.0.0.1:8765';
const dir=process.env.STUDIO_EVIDENCE||'/tmp/studio-evidence';
await mkdir(dir,{recursive:true});
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:1440,height:900}});
const errors=[];
page.on('pageerror',e=>errors.push(e.message));
const response=await page.goto(url,{waitUntil:'networkidle'});
assert.equal(response.status(),200);
await page.locator('#state[data-kind=ready]').waitFor({timeout:30000});
const catalog=await (await page.request.get(new URL('live_catalog.json',url.endsWith('/')?url:url+'/').href)).json();
assert.equal(await page.locator('#assets button').count(),catalog.assets.length);
const observed=[];
let lightingEvidence=null;
for(const a of catalog.assets){
 const paths=[...new Set([a.preview?.resource,...(a.outputs||[]).map(x=>x.path)].filter(p=>p&&/\.glb$/i.test(p)&&catalog.resources[p]?.status!=='missing'))];
 if(!paths.length)continue;
 await page.locator('#assets button').filter({hasText:a.id}).first().click();
 for(const p of paths){
  await page.locator('#variant').selectOption(p);
  await page.waitForFunction(p=>document.querySelector('#viewport').dataset.resource===p&&document.querySelector('#state').dataset.kind==='ready',p,{timeout:30000});
  assert.equal(await page.locator('#viewport').getAttribute('data-sha256'),catalog.resources[p].sha256);
  observed.push(p);
 }
 if(observed.length===paths.length){
   const diagnostics=()=>page.locator('#viewport').getAttribute('data-lighting').then(JSON.parse);
   const info=await diagnostics();
   for(const key of ['environment','aces','srgb','antialias','softShadow','shadows','grid','floor'])assert.equal(info[key],true,key);
   assert.match(info.hdr,/^[a-f0-9]{64}$/);
   assert.match(await page.locator('#grid-scale').textContent(),/m \/ célula/);
   await page.waitForTimeout(300);
   await page.screenshot({path:dir+'/studio-model.png'});
   await page.locator('#grid').uncheck();await page.locator('#shadows').uncheck();
   let off=await diagnostics();assert.equal(off.grid,false);assert.equal(off.shadows,false);
   await page.locator('#exposure').fill('1.5');assert.equal((await diagnostics()).exposure,1.5);
   await page.waitForTimeout(300);
   await page.screenshot({path:dir+'/studio-lighting-alternate.png'});
   await page.locator('#grid').check();await page.locator('#shadows').check();await page.locator('#exposure').fill('1');
   lightingEvidence=info;
 }
}
assert.equal(new Set(observed).size,Object.keys(catalog.resources).filter(p=>p.endsWith('.glb')&&catalog.resources[p].status!=='missing').length);
await page.locator('#search').fill('no-result-unique-qa');
assert.equal(await page.locator('#assets button').count(),0);
await page.locator('#search').fill('');
const procedural=catalog.assets.find(a=>!(a.outputs||[]).length&&!a.preview?.resource);
assert(procedural);
await page.locator('#assets button').filter({hasText:procedural.id}).first().click();
await page.locator('#state[data-kind=unavailable]').waitFor();
await page.screenshot({path:dir+'/studio-unavailable.png'});
assert(lightingEvidence);
assert.equal(JSON.parse(await page.locator('#viewport').getAttribute('data-lighting')).floor,false);
assert.deepEqual(errors,[]);
await writeFile(dir+'/report.json',JSON.stringify({revision:catalog.revision,assets:catalog.assets.length,glbLoaded:[...new Set(observed)],browser:browser.version(),errors,lighting:lightingEvidence,visualApproval:false},null,2));
console.log('STUDIO_BROWSER_PASS',new Set(observed).size,'GLB');
await browser.close();
