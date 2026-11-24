import {chromium} from 'playwright';
import assert from 'node:assert/strict';
const url=process.env.STUDIO_URL||'http://127.0.0.1:8766';
const origin=new URL(url).origin;
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage();
 const external=[];
 await page.route('**/*',route=>{
  const u=new URL(route.request().url());
  if(['http:','https:'].includes(u.protocol)&&u.origin!==origin){external.push(u.href);return route.abort();}
  return route.continue();
 });
 await page.goto(url);
 await page.locator('#state[data-kind=ready]').waitFor({timeout:30000});
 assert.equal(await page.locator('#inspection').isVisible(),true);
 assert(JSON.parse(await page.locator('#viewport').getAttribute('data-inspection')).triangles>0);
 const catalog=await (await page.request.get(origin+'/live_catalog.json')).json();
 assert.equal(catalog.runtime_views.count,5);
 const map=catalog.assets.find(a=>a.id==='map:campo_de_testes');
 await page.locator('#assets button').filter({hasText:map.id}).first().click();
 await page.locator('#runtime-view').selectOption('map_collision');
 await page.waitForFunction(()=>document.querySelector('#viewport').dataset.runtimeView==='map_collision');
 assert.deepEqual(external,[]);
 console.log('STUDIO_OFFLINE_EXTRACTED_PASS real GLB and Godot collision view, no network');
}finally{await browser.close();}
