import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
const url=process.env.STUDIO_URL||'http://127.0.0.1:8765';
const dir=process.env.STUDIO_EVIDENCE||'/tmp/studio-evidence';
await mkdir(dir,{recursive:true});
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:1440,height:900}});
const errors=[],externalRequests=[];
const origin=new URL(url).origin;
page.on('request',r=>{const u=new URL(r.url());if(['http:','https:'].includes(u.protocol)&&u.origin!==origin)externalRequests.push(r.url());});
await page.route('**/*',r=>{const u=new URL(r.request().url());return ['http:','https:'].includes(u.protocol)&&u.origin!==origin?r.abort():r.continue();});
let inspectionEvidence=null;
page.on('pageerror',e=>errors.push(e.message));
const response=await page.goto(url,{waitUntil:'networkidle'});
assert.equal(response.status(),200);
await page.locator('#state[data-kind=ready]').waitFor({timeout:30000});
const catalog=await (await page.request.get(new URL('live_catalog.json',url.endsWith('/')?url:url+'/').href)).json();
assert.equal(await page.locator('#assets button').count(),catalog.assets.length);
if(process.env.REQUIRE_RUNTIME_VIEWS==='1'){
 assert(catalog.runtime&&catalog.runtime.commit===catalog.revision);
 assert.equal(Object.keys(catalog.runtime_samples).length,catalog.runtime.samples);
 const sampled=catalog.assets.find(a=>a.runtime_samples?.some(id=>catalog.runtime_samples[id]));
 assert(sampled);
 await page.locator('#assets button').filter({hasText:sampled.id}).first().click();
 assert.equal(await page.locator('#runtime-sample').isDisabled(),false);
 const id=await page.locator('#runtime-sample').inputValue();
 assert.match(await page.locator('#runtime-sample-info').textContent(),/subárvore inteira/);
 assert((await page.locator('#runtime-sample-info').textContent()).includes('Colisões ativas: '+catalog.runtime_samples[id].enabled_colliders));
 assert(catalog.geometry_payload&&catalog.composition_payload);
 let compositionSamples=null;
 for(const [name,hash] of [[catalog.geometry_payload,catalog.geometry_payload_sha256],[catalog.composition_payload,catalog.composition_payload_sha256]]){
   const resp=await page.request.get(new URL(name,url.endsWith('/')?url:url+'/').href);
   assert.equal(resp.status(),200);
   const bytes=await resp.body();
   assert.equal(createHash('sha256').update(bytes).digest('hex'),hash);
   const payload=JSON.parse(bytes.toString('utf8'));
   assert.equal(payload.revision,catalog.revision);
   if(name===catalog.geometry_payload){
     assert.equal(Object.keys(payload.buffers).length,Object.keys(catalog.geometry_index).length);
     for(const [digest,buffer] of Object.entries(payload.buffers)){
       const data=Buffer.from(buffer.data,'base64');
       assert.equal(data.length,buffer.bytes);
       assert.equal(createHash('sha256').update(data).digest('hex'),digest);
     }
   }else{
     assert.equal(payload.samples.length,catalog.runtime.samples);
     compositionSamples=payload.samples;
     assert.equal(payload.registered_world_lods.length,23);
     const posts=payload.registered_world_lods.filter(a=>a.family==='light_post');
     assert.equal(posts.length,4);
     for(const p of posts){
       assert.equal(p.collision_policy,'nonblocking');
       assert.equal(p.blocker,null);assert.equal(p.shape,null);
       assert.equal(p.parts.length,3);
       assert.deepEqual(p.levels.map(l=>l.assembly_triangles),[1632,360,144]);
     }
   }
 }
 console.log('STUDIO_RUNTIME_PAYLOAD_PASS',Object.keys(catalog.geometry_index).length,'buffers');
 // 00-34: exact QA scopes must reconcile with the original sample payload.
 // Older captures are not sufficient for the current integrated browser gate.
 const expectedScopes={"player_capsule":"player:collision","muzzle_mesh":"effect:muzzle","scope_canvas":"effect:scope_overlay","turret":"object:turret","loot_weapon":"object:loot","loot_ammo":"object:loot","grenade_body":"object:grenade","grenade_fx":"effect:grenade","blood":"effect:blood","shot_fx":"effect:combat","enemy_tracer":"effect:enemy_tracer","airstrike_marker":"effect:combat","airstrike_impact":"effect:combat"};
 const seenRoles=new Set(),scopeExamples=new Map();
 assert.equal(catalog.approved,false);
 const scopedAssets=catalog.assets.filter(a=>a.runtime_scope_status==='qa_scoped_nodes');
 assert.deepEqual(scopedAssets.map(a=>a.id).sort(),[...new Set(Object.values(expectedScopes))].sort());
 assert(compositionSamples,'missing composition samples for scope reconciliation');
 const sampleById=new Map(compositionSamples.map(s=>[s.id,s]));
 let scopeCount=0;
 for(const a of scopedAssets){
   assert.equal(a.validation.approved,false);
   assert(a.runtime_scopes?.length,a.id);
   const pairs=new Set();
   for(const scope of a.runtime_scopes){
     assert.equal(expectedScopes[scope.role],a.id);
     assert.equal(scope.family,a.id);
     assert.equal(scope.scope,'qa_selected_actual_nodes');
     assert.equal(scope.approved,false);
     assert(a.runtime_samples.includes(scope.sample));
     const pair=JSON.stringify([scope.sample,scope.role]);assert(!pairs.has(pair));pairs.add(pair);
     const sample=sampleById.get(scope.sample);assert(sample,scope.sample);
     const source=sample.asset_scopes?.find(s=>s.role===scope.role);
     assert(source,scope.role);
     assert.deepEqual(scope.roots,source.roots);
     const paths=new Set(sample.nodes.map(n=>n.path));
     assert(scope.roots.length&&scope.roots.every(p=>paths.has(p)));
     assert(scope.node_paths.length&&scope.node_paths.every(p=>paths.has(p)));
     seenRoles.add(scope.role);
     if(!scopeExamples.has(scope.role))scopeExamples.set(scope.role,{asset:a,scope});
     scopeCount++;
   }
 }
 const expectedCount=compositionSamples.reduce((n,s)=>n+(s.asset_scopes?.length||0),0);
 assert.equal(scopeCount,expectedCount);
 assert.deepEqual([...seenRoles].sort(),Object.keys(expectedScopes).sort());
 // Check one real sample of every role through the same UI used by reviewers.
 for(const {asset,scope} of scopeExamples.values()){
   await page.locator('#assets button').filter({hasText:asset.id}).first().click();
   await page.locator('#runtime-sample').selectOption(scope.sample);
   const info=await page.locator('#runtime-sample-info').textContent();
   assert(info.includes('Escopo específico: '+scope.role+' · '+scope.mesh_nodes+' malhas ('+scope.visible_mesh_nodes+' visíveis) · '+scope.collisions.length+' colisores · '+scope.lights+' luzes'),scope.role);
   assert(info.includes('Nós reais: '+scope.roots.join(', ')),scope.role);
   assert(info.includes('subárvore inteira'),scope.role);
   for(const c of scope.collisions)assert(info.includes('Colisor '+c.path+' · '+c.shape.class+' · camada '+c.layer+' · máscara '+c.mask),scope.role);
   if(scope.canvas_visible!==null)assert(info.includes('Sobreposição visível: '+String(scope.canvas_visible)),scope.role);
 }
 console.log('STUDIO_RUNTIME_SCOPES_PASS',seenRoles.size,'roles',scopedAssets.length,'families',scopeCount,'scopes');
 assert(catalog.surface_payload&&catalog.surface_payload_sha256,'missing portable runtime surface payload');
 if(catalog.surface_payload){
   const raw=await page.request.get(new URL(catalog.surface_payload,url.endsWith('/')?url:url+'/').href);assert.equal(raw.status(),200);const bytes=await raw.body();assert.equal(createHash('sha256').update(bytes).digest('hex'),catalog.surface_payload_sha256);const native=JSON.parse(bytes.toString('utf8'));assert.equal(native.coverage.length,86);assert(Object.keys(catalog.geometry_index).every(h=>native.buffers[h]));
   const scenarios=[['map_briefing','map:campo_de_testes'],['fps_rifle___hip','viewmodel:assembly'],['enemy_soldier_rifle','enemy:legacy'],['enemy_quaternius_experimental','character:quaternius_equipment'],['loot_ammo','object:loot'],['turret','object:turret']];
   for(const [id,family] of scenarios){
     const asset=catalog.assets.find(a=>a.id===family&&a.runtime_samples?.includes(id));assert(asset,id);
     await page.locator('#assets button').filter({hasText:asset.id}).first().click();
     await page.locator('#runtime-sample').selectOption(id);
     await page.locator('#open-composition').click();
     await page.waitForFunction(id=>document.querySelector('#state').dataset.kind==='error'||(JSON.parse(document.querySelector('#viewport').dataset.composition||'{}').id===id&&document.querySelector('#state').dataset.kind==='ready'),id,{timeout:60000});
     assert.equal(await page.locator('#state').getAttribute('data-kind'),'ready',await page.locator('#state').textContent());
     const stats=JSON.parse(await page.locator('#viewport').getAttribute('data-composition'));
     const expected=catalog.surface_coverage.find(s=>s.id===id);
     assert.equal(stats.surfaces,expected.surfaces);assert.equal(stats.triangles,expected.visible_triangles);assert(stats.maxMatrixError<1e-5);
     assert.equal(await page.locator('#title').textContent(),'Composição · '+id);assert(await page.locator('#pose-x').isDisabled());
     await page.screenshot({path:dir+'/composition-'+id+'.png'});
     console.log('STUDIO_COMPOSITION_PASS',JSON.stringify(stats));
     if(id==='map_briefing'){
       assert.equal(catalog.composition_views?.length,1);
       await page.locator('#compare-composition').click();
       await page.waitForFunction(()=>document.querySelector('#viewport').dataset.comparison||document.querySelector('#state').dataset.kind==='error',null,{timeout:30000});
       const comparison=JSON.parse(await page.locator('#viewport').getAttribute('data-comparison'));
       assert(comparison.landmarks>=4&&comparison.maxProjectionErrorPx<=1);
       await page.screenshot({path:dir+'/composition-camera-comparison.png'});
       const png=await page.locator('.composition-comparison img').nth(1).getAttribute('src');
       await writeFile(dir+'/composition-map-native-camera.png',Buffer.from(png.split(',')[1],'base64'));
       console.log('STUDIO_CAMERA_COMPARISON_PASS',JSON.stringify(comparison));
       await page.locator('#compare-composition').click();
     }
   }
   const all=await page.evaluate(async ids=>{
     const {createRuntimeComposition}=await import('./runtime-composition.js');
     const catalog=await fetch('./live_catalog.json').then(r=>r.json());
     const build=createRuntimeComposition(catalog),rows=[];
     for(const id of ids){
       const {scene,stats}=await build(id);
       rows.push({id,surfaces:stats.surfaces,triangles:stats.triangles,maxMatrixError:stats.maxMatrixError});
       const geos=new Set(),mats=new Set(),textures=new Set();
       scene.traverse(o=>{if(o.geometry)geos.add(o.geometry);if(o.material){mats.add(o.material);for(const t of Object.values(o.material))if(t?.isTexture)textures.add(t);}});
       geos.forEach(g=>g.dispose());mats.forEach(m=>m.dispose());textures.forEach(t=>t.dispose());
     }
     return rows;
   },catalog.surface_coverage.map(s=>s.id));
   assert.equal(all.length,catalog.runtime.samples);
   for(const row of all){const x=catalog.surface_coverage.find(s=>s.id===row.id);assert.equal(row.surfaces,x.surfaces);assert.equal(row.triangles,x.visible_triangles);assert(row.maxMatrixError<1e-5);}
   await writeFile(dir+'/composition-coverage.json',JSON.stringify(all,null,2));
   console.log('STUDIO_COMPOSITION_COVERAGE_PASS',all.length);
 }
 console.log('STUDIO_RECONCILED_RUNTIME_PASS',catalog.runtime.samples,'samples');
}
if(process.env.REQUIRE_RUNTIME_VIEWS==='1'){
 const selectAsset=id=>page.locator('#assets button[data-asset="'+id+'"]').click();
 const selectComposition=async id=>{
  await page.locator('#runtime-sample').selectOption(id);
  await page.locator('#open-composition').click();
  await page.waitForFunction(id=>JSON.parse(document.querySelector('#viewport').dataset.composition||'{}').id===id,id);
 };
 const viewport=page.locator('#viewport');
 const inspect=()=>viewport.getAttribute('data-inspection').then(JSON.parse);
 await selectAsset('viewmodel:assembly');
 await page.locator('#runtime-view').selectOption('player_tps');
 await page.waitForFunction(()=>document.querySelector('#viewport').dataset.runtimeView==='player_tps');
 const tps=catalog.assets.find(a=>a.id==='viewmodel:assembly').runtime_views.find(v=>v.id==='player_tps');
 assert.equal(tps.context.body_parent,tps.context.player_path);
 assert.equal(await viewport.getAttribute('data-sha256'),tps.sha256);
 await page.screenshot({path:dir+'/player-tps.png'});

 await selectAsset('map:campo_de_testes');
 await selectComposition('map_briefing');
 await page.locator('#runtime-shapes').check();
 assert.equal(Number(await viewport.getAttribute('data-collision-shapes')),catalog.runtime_samples.map_briefing.enabled_colliders);
 const initial=(await inspect()).triangles;
 const levels=[];
 for(const index of [1,2,0]){
  await page.locator('#lod-level').selectOption(String(index));
  await page.waitForFunction(index=>JSON.parse(document.querySelector('#viewport').dataset.registeredLod||'{}').level===index,index);
  const row=JSON.parse(await viewport.getAttribute('data-registered-lod'));
  assert(row.shape);
  levels.push(row);
  assert.equal(Number(await viewport.getAttribute('data-collision-shapes')),catalog.runtime_samples.map_briefing.enabled_colliders);
  await page.screenshot({path:dir+'/registered-lod-'+index+'.png'});
 }
 assert(levels[0].triangles>levels[1].triangles&&levels[2].triangles>levels[0].triangles);
 assert(levels.every(row=>row.shape===levels[0].shape));
 assert.equal((await inspect()).triangles,initial);
 await page.locator('#runtime-shapes').uncheck();
 assert.equal(await viewport.getAttribute('data-collision-shapes'),null);
 console.log('STUDIO_REGISTERED_LOD_PASS',levels.map(row=>row.triangles));

 async function assertClip(jointName){
  const node=page.locator('#node-select option').filter({hasText:jointName}).first();
  await page.locator('#node-select').selectOption(await node.getAttribute('value'));
  const rest=(await inspect()).pose;
  await page.locator('#clip-select').selectOption('0');
  await page.locator('#clip-time').fill('0.5');
  assert.notDeepEqual((await inspect()).pose,rest);
  await page.screenshot({path:dir+'/clip-'+jointName.split('/').at(-1)+'.png'});
  await page.locator('#clip-play').click();
  await page.waitForFunction(()=>JSON.parse(document.querySelector('#viewport').dataset.inspection).clipTime!==.5);
  await page.locator('#pose-reset').click();
  assert.deepEqual((await inspect()).pose,rest);
 }
 await selectAsset('character:quaternius_base_male');
 await page.locator('#state[data-kind=ready]').waitFor();
 await assertClip('lowerarm_l');
 await selectAsset('ally:legacy');
 await selectComposition('ally');
 await assertClip('LeftShoulder/Elbow');
 console.log('STUDIO_AUTHORED_INSPECTION_CLIPS_PASS pilot bone and runtime joint');
}
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
   const inspectionState=()=>page.locator('#viewport').getAttribute('data-inspection').then(JSON.parse);
   const initial=await inspectionState();
   assert(initial.vertices>0&&initial.triangles>0&&initial.materials>0);
   assert(initial.dimensions.some(x=>x>0));
   assert.equal(await page.locator('#inspection').isVisible(),true);
   for(const mode of ['solid','wireframe','textured']){
     await page.locator('#inspection-mode').selectOption(mode);
     const current=await inspectionState();
     assert.equal(current.mode,mode);assert.equal(current.vertices,initial.vertices);assert.equal(current.triangles,initial.triangles);assert.equal(current.materials,initial.materials);
     await page.screenshot({path:dir+'/studio-inspection-'+mode+'.png'});
   }
   assert.match(await page.locator('#material-info').textContent(),/type/);
   await page.locator('#uv-channel').selectOption('uv1');await page.locator('#uv-channel').selectOption('uv');
   assert.match(await page.locator('#uv-summary').textContent(),/triângulos UV|Canal ausente/);
   await page.locator('#pivots-toggle').check();assert((await inspectionState()).helpers>0);
   await page.locator('#normals-toggle').check();assert((await inspectionState()).helpers>0);
   await page.screenshot({path:dir+'/studio-inspection-helpers.png'});
   await page.locator('#pivots-toggle').uncheck();await page.locator('#normals-toggle').uncheck();
   assert.equal((await inspectionState()).helpers,0);
   await page.locator('#node-select').selectOption('0');
   const beforePose=(await inspectionState()).pose;
   await page.locator('#pose-y').fill('30');assert.equal((await inspectionState()).pose[1],30);
   await page.locator('#pose-reset').click();assert.deepEqual((await inspectionState()).pose,beforePose);
   if(initial.clips>0){
     await page.locator('#clip-select').selectOption('0');
     const max=Number(await page.locator('#clip-time').getAttribute('max'));
     if(max>.05){await page.locator('#clip-time').fill(String(max/2));assert((await inspectionState()).clipTime>0);}
     await page.locator('#clip-play').click();await page.waitForTimeout(200);assert.equal((await inspectionState()).playing,true);
     await page.locator('#pose-reset').click();assert.equal((await inspectionState()).playing,false);
   }
   const [download]=await Promise.all([page.waitForEvent('download'),page.locator('#screenshot').click()]);
   await download.saveAs(dir+'/studio-user-screenshot.png');
   const png=await readFile(dir+'/studio-user-screenshot.png');
   assert.equal(png.subarray(0,8).toString('hex'),'89504e470d0a1a0a');
   assert(png.readUInt32BE(16)>100&&png.readUInt32BE(20)>100);
   inspectionEvidence={initial,afterReset:await inspectionState(),pngBytes:png.length};
   console.log('STUDIO_INSPECTION_PASS modes UV metrics pivots pose and PNG');
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
 assert.equal(captures.length,6);
 assert(captures.includes('player_tps'));
 assert(captures.includes('map_collision'));
 const collision=catalog.assets.flatMap(a=>a.runtime_views||[]).find(v=>v.id==='map_collision');
 assert(collision.context.debug_mesh_count>0&&collision.context.collision_shapes.length===collision.context.debug_mesh_count);
 console.log('STUDIO_RUNTIME_VIEWS_PASS',captures.join(','));
}else if(process.env.REQUIRE_RUNTIME_VIEWS==='1')throw Error('missing Godot captures');
// Browser-only neutral test fixture: never written into the production catalog or package.
const dependencyPage=await browser.newPage({viewport:{width:1280,height:800}});
const fixturePath='qa-fixture/models/panel.gltf',bufferPath='qa-fixture/buffers/qa mesh.bin';
const buffer=Buffer.alloc(100);
[-1,0,0,1,0,0,0,1,0].forEach((v,i)=>buffer.writeFloatLE(v,i*4));
[0,1,2].forEach((v,i)=>buffer.writeUInt16LE(v,36+i*2));
[0,0,1,0,.5,1].forEach((v,i)=>buffer.writeFloatLE(v,44+i*4));
[0,1,0,0,0,1,0,0].forEach((v,i)=>buffer.writeFloatLE(v,68+i*4));
const fixture=Buffer.from(JSON.stringify({asset:{version:'2.0'},scene:0,scenes:[{nodes:[0]}],nodes:[{name:'animated_panel',mesh:0}],
 meshes:[{primitives:[{attributes:{POSITION:0,TEXCOORD_0:2},indices:1,material:0}]}],
 materials:[{name:'qa_material',pbrMetallicRoughness:{baseColorFactor:[.2,.6,.8,1],metallicFactor:0,roughnessFactor:.7}}],
 buffers:[{uri:'../buffers/qa%20mesh.bin',byteLength:100}],
 bufferViews:[{buffer:0,byteOffset:0,byteLength:36,target:34962},{buffer:0,byteOffset:36,byteLength:6,target:34963},{buffer:0,byteOffset:44,byteLength:24,target:34962},{buffer:0,byteOffset:68,byteLength:8},{buffer:0,byteOffset:76,byteLength:24}],
 accessors:[{bufferView:0,componentType:5126,count:3,type:'VEC3',min:[-1,0,0],max:[1,1,0]},{bufferView:1,componentType:5123,count:3,type:'SCALAR'},{bufferView:2,componentType:5126,count:3,type:'VEC2'},{bufferView:3,componentType:5126,count:2,type:'SCALAR',min:[0],max:[1]},{bufferView:4,componentType:5126,count:2,type:'VEC3'}],
 animations:[{name:'qa_move',samplers:[{input:3,output:4,interpolation:'LINEAR'}],channels:[{sampler:0,target:{node:0,path:'translation'}}]}]}));
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
const fixtureState=()=>dependencyPage.locator('#viewport').getAttribute('data-inspection').then(JSON.parse);
const fixtureMetrics=await fixtureState();
assert.equal(fixtureMetrics.vertices,3);assert.equal(fixtureMetrics.triangles,1);assert.equal(fixtureMetrics.materials,1);assert.equal(fixtureMetrics.uvMeshes,1);assert.equal(fixtureMetrics.clips,1);
assert.deepEqual(fixtureMetrics.dimensions,[2,1,0]);assert.match(await dependencyPage.locator('#uv-summary').textContent(),/1 \/ 1 triângulos UV/);
await dependencyPage.locator('#clip-select').selectOption('0');
await dependencyPage.locator('#clip-time').fill('0.5');
const mid=await fixtureState();assert.equal(mid.clipTime,.5);assert.equal(mid.min[0],-.5);
await dependencyPage.locator('#clip-play').click();
await dependencyPage.waitForFunction(()=>JSON.parse(document.querySelector('#viewport').dataset.inspection).clipTime>.5);
await dependencyPage.locator('#pose-reset').click();
assert.deepEqual((await fixtureState()).min,fixtureMetrics.min);
console.log('STUDIO_ANIMATION_METRICS_PASS known fixture counts and interpolated transform');
tamper=true;
await dependencyPage.locator('#assets button').filter({hasText:'qa:dependency_fixture'}).click();
await dependencyPage.locator('#state[data-kind=error]').waitFor({timeout:30000});
assert.match(await dependencyPage.locator('#state').textContent(),/Hash divergente/);
assert.equal(await dependencyPage.locator('#viewport').getAttribute('data-resource'),null);
assert.equal(bufferRequests,2);
await dependencyPage.close();
console.log('STUDIO_EXTERNAL_DEPENDENCY_PASS verified bytes and tamper rejection');
assert.deepEqual(errors,[]);assert.deepEqual(externalRequests,[]);assert(inspectionEvidence);console.log('STUDIO_LOCAL_ONLY_PASS no external HTTP requests');
await writeFile(dir+'/report.json',JSON.stringify({revision:catalog.revision,assets:catalog.assets.length,glbLoaded:[...new Set(observed)],browser:browser.version(),errors,lighting:lightingEvidence,camera:cameraEvidence,runtimeViews:captures,inspection:inspectionEvidence,externalRequests,visualApproval:false},null,2));
console.log('STUDIO_BROWSER_PASS',new Set(observed).size,'GLB');
await browser.close();
