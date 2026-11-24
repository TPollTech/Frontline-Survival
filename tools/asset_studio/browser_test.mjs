import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
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
let lightingEvidence=null,cameraEvidence=null;
const cameraState=()=>page.locator('#viewport').getAttribute('data-camera').then(JSON.parse);
const assertFit=async()=>{const c=await cameraState();assert(c.damping&&c.pan&&c.zoom&&c.depthInside);assert(c.maxNdc<=0.88,'bounding box clipped: '+c.maxNdc);assert(c.near>0&&c.far>c.near);return c;};
const distance=(a,b)=>Math.hypot(...a.map((x,i)=>x-b[i]));
for(const a of catalog.assets){
 const paths=[...new Set([a.preview?.resource,...(a.outputs||[]).map(x=>x.path)].filter(p=>p&&/\.glb$/i.test(p)&&catalog.resources[p]?.status!=='missing'))];
 if(!paths.length)continue;
 await page.locator('#assets button').filter({hasText:a.id}).first().click();
 for(const p of paths){
  await page.locator('#variant').selectOption(p);
  await page.waitForFunction(p=>document.querySelector('#viewport').dataset.resource===p&&document.querySelector('#state').dataset.kind==='ready',p,{timeout:30000});
  assert.equal(await page.locator('#viewport').getAttribute('data-sha256'),catalog.resources[p].sha256);
  await assertFit();
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
   const home=await assertFit();
   const canvas=page.locator('#viewport canvas');
   const r=await canvas.boundingBox(),x=r.x+r.width*.5,y=r.y+r.height*.5;
   await page.mouse.move(x,y);await page.mouse.down();await page.mouse.move(x+95,y+35,{steps:8});await page.mouse.up();
   await page.waitForFunction(home=>JSON.parse(document.querySelector('#viewport').dataset.camera).position.some((v,i)=>Math.abs(v-home.position[i])>home.distance*.01),home);
   const rotated=await cameraState();assert(distance(rotated.position,home.position)>home.distance*.01);
   await page.mouse.move(x,y);await page.mouse.down({button:'right'});await page.mouse.move(x+60,y+25,{steps:8});await page.mouse.up({button:'right'});
   await page.waitForFunction(home=>JSON.parse(document.querySelector('#viewport').dataset.camera).target.some((v,i)=>Math.abs(v-home.target[i])>home.distance*.005),home);
   const panned=await cameraState();assert(distance(panned.target,home.target)>home.distance*.005);
   await page.mouse.wheel(0,-300);
   await page.waitForFunction(d=>JSON.parse(document.querySelector('#viewport').dataset.camera).distance<d*.98,panned.distance);
   await page.screenshot({path:dir+'/studio-camera-interaction.png'});
   await page.locator('#reset').click();
   await page.waitForTimeout(300);
   const reset=await assertFit();assert(distance(reset.position,home.position)<home.distance*1e-5);assert(distance(reset.target,home.target)<home.distance*1e-5);
   await page.locator('#zoom-in').click();assert((await cameraState()).distance<reset.distance*.9);
   await page.locator('#zoom-out').click();assert(Math.abs((await cameraState()).distance-reset.distance)<reset.distance*1e-5);
   await page.locator('#reset').click();
   await page.setViewportSize({width:520,height:900});
   await page.waitForFunction(a=>{const c=JSON.parse(document.querySelector('#viewport').dataset.camera);const v=document.querySelector('#viewport');return Math.abs(c.aspect-v.clientWidth/v.clientHeight)<.01&&Math.abs(c.aspect-a)>.03;},home.aspect);
   const narrow=await assertFit();await page.screenshot({path:dir+'/studio-camera-narrow.png'});
   await page.setViewportSize({width:1440,height:900});
   await page.waitForFunction(a=>Math.abs(JSON.parse(document.querySelector('#viewport').dataset.camera).aspect-a)<.01,home.aspect);
   await assertFit();
   const views={front:[0,0,-1],back:[0,0,1],left:[-1,0,0],right:[1,0,0],top:[0,1,0],bottom:[0,-1,0]};
   const viewEvidence={};
   for(const [name,axis] of Object.entries(views)){
     await page.locator('#view').selectOption(name);
     const c=await assertFit();
     assert.equal(c.projection,'orthographic');assert.equal(c.mode,name);assert.equal(c.rotate,false);
     assert(distance(c.direction,axis)<1e-5,'wrong axis '+name);
     assert.equal((await diagnostics()).floor,name!=='bottom');
     await page.screenshot({path:dir+'/studio-view-'+name+'.png'});
     viewEvidence[name]=c;
   }
   const bottom=await cameraState();
   await page.locator('#zoom-in').click();assert((await cameraState()).cameraZoom>bottom.cameraZoom);
   await page.locator('#reset').click();assert.equal((await assertFit()).cameraZoom,1);
   await page.locator('#view').selectOption('perspective');assert.equal((await assertFit()).projection,'perspective');
   assert.equal((await diagnostics()).floor,true);
   await page.locator('#fullscreen').click();
   await page.waitForFunction(()=>document.fullscreenElement===document.querySelector('.workspace'));
   await page.waitForFunction(()=>{const c=JSON.parse(document.querySelector('#viewport').dataset.camera),v=document.querySelector('#viewport');return Math.abs(c.aspect-v.clientWidth/v.clientHeight)<.01;});
   const full=await assertFit();await page.screenshot({path:dir+'/studio-fullscreen.png'});
   await page.locator('#fullscreen').click();await page.waitForFunction(()=>!document.fullscreenElement);
   await page.waitForFunction(()=>{const c=JSON.parse(document.querySelector('#viewport').dataset.camera),v=document.querySelector('#viewport');return Math.abs(c.aspect-v.clientWidth/v.clientHeight)<.01;});
   await assertFit();
   cameraEvidence={home,rotated,panned,reset,narrow,views:viewEvidence,fullscreen:full};
   console.log('STUDIO_VIEWS_PASS six orthographic axes perspective fullscreen');
   console.log('STUDIO_CAMERA_PASS orbit pan wheel reset resize');
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
assert(lightingEvidence);assert(cameraEvidence);assert.equal(await page.locator('#reset').isDisabled(),true);assert.equal(await page.locator('#zoom-in').isDisabled(),true);
assert.equal(JSON.parse(await page.locator('#viewport').getAttribute('data-lighting')).floor,false);
const captures=[];
if(catalog.runtime_views){
 assert.equal(catalog.runtime_views.revision,catalog.revision);
 for(const a of catalog.assets.filter(a=>a.runtime_views?.length)){
  await page.locator('#assets button').filter({hasText:a.id}).first().click();
  for(const v of a.runtime_views){
   await page.locator('#runtime-view').selectOption(v.id);
   await page.waitForFunction(id=>document.querySelector('#viewport').dataset.runtimeView===id&&document.querySelector('#state').dataset.kind==='ready',v.id);
   assert.equal(await page.locator('#viewport').getAttribute('data-sha256'),v.sha256);
   assert.equal(await page.locator('#viewport img.runtime-capture').evaluate(i=>i.naturalWidth),v.width);
   assert.equal(await page.locator('#view').isDisabled(),true);
   await page.screenshot({path:dir+'/studio-godot-'+v.id+'.png'});
   captures.push(v.id);
  }
 }
 assert.equal(captures.length,4);
 console.log('STUDIO_RUNTIME_VIEWS_PASS',captures.join(','));
}else if(process.env.REQUIRE_RUNTIME_VIEWS==='1')throw Error('missing Godot captures');
// Browser-only neutral test fixture: never written into the production catalog or package.
const dependencyPage=await browser.newPage({viewport:{width:1280,height:800}});
const fixturePath='qa-fixture/models/panel.gltf',bufferPath='qa-fixture/buffers/qa mesh.bin';
const buffer=Buffer.alloc(44);
[-1,0,0,1,0,0,0,1,0].forEach((v,i)=>buffer.writeFloatLE(v,i*4));
[0,1,2].forEach((v,i)=>buffer.writeUInt16LE(v,36+i*2));
const fixture=Buffer.from(JSON.stringify({asset:{version:'2.0'},scene:0,scenes:[{nodes:[0]}],nodes:[{mesh:0}],
 meshes:[{primitives:[{attributes:{POSITION:0},indices:1}]}],
 buffers:[{uri:'../buffers/qa%20mesh.bin',byteLength:44}],
 bufferViews:[{buffer:0,byteOffset:0,byteLength:36,target:34962},{buffer:0,byteOffset:36,byteLength:6,target:34963}],
 accessors:[{bufferView:0,componentType:5126,count:3,type:'VEC3',min:[-1,0,0],max:[1,1,0]},{bufferView:1,componentType:5123,count:3,type:'SCALAR'}]}));
const hash=b=>createHash('sha256').update(b).digest('hex');
const fixtureCatalog={kind:catalog.kind,schema_version:catalog.schema_version,revision:catalog.revision,
 assets:[{id:'qa:dependency_fixture',category:'model',usage:'test_only',source:{path:fixturePath},
 outputs:[{path:fixturePath}],preview:{resource:fixturePath},validation:{approved:false}}],
 resources:{[fixturePath]:{status:'new',sha256:hash(fixture),gltf_dependencies:[{uri:'../buffers/qa%20mesh.bin',path:bufferPath}]},
 [bufferPath]:{status:'new',sha256:hash(buffer)}}};
let tamper=false,bufferRequests=0;
await dependencyPage.route('**/live_catalog.json',route=>route.fulfill({json:fixtureCatalog}));
await dependencyPage.route('**/qa-fixture/**',route=>{
 const p=decodeURIComponent(new URL(route.request().url()).pathname);
 if(p.endsWith('/'+fixturePath))return route.fulfill({body:fixture,contentType:'model/gltf+json'});
 if(p.endsWith('/'+bufferPath)){
  bufferRequests++;
  const data=Buffer.from(buffer);
  if(tamper)data[0]^=1;
  return route.fulfill({body:data,contentType:'application/octet-stream'});
 }
 return route.abort();
});
await dependencyPage.goto(url,{waitUntil:'networkidle'});
await dependencyPage.locator('#assets button').filter({hasText:'qa:dependency_fixture'}).click();
await dependencyPage.locator('#state[data-kind=ready]').waitFor({timeout:30000});
assert.equal(await dependencyPage.locator('#viewport').getAttribute('data-sha256'),hash(fixture));
assert.equal(bufferRequests,1,'must not refetch verified external bytes');
tamper=true;
await dependencyPage.locator('#assets button').filter({hasText:'qa:dependency_fixture'}).click();
await dependencyPage.locator('#state[data-kind=error]').waitFor({timeout:30000});
assert.match(await dependencyPage.locator('#state').textContent(),/Hash divergente/);
assert.equal(await dependencyPage.locator('#viewport').getAttribute('data-resource'),null);
assert.equal(bufferRequests,2);
await dependencyPage.close();
console.log('STUDIO_EXTERNAL_DEPENDENCY_PASS verified bytes and tamper rejection');
assert.deepEqual(errors,[]);
await writeFile(dir+'/report.json',JSON.stringify({revision:catalog.revision,assets:catalog.assets.length,glbLoaded:[...new Set(observed)],browser:browser.version(),errors,lighting:lightingEvidence,camera:cameraEvidence,runtimeViews:captures,visualApproval:false},null,2));
console.log('STUDIO_BROWSER_PASS',new Set(observed).size,'GLB');
await browser.close();
