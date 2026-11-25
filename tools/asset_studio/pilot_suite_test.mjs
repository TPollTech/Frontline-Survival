import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
const directory=process.env.FRONTLINE_PILOT_DIR;
const read=async p=>JSON.parse(await readFile(p,'utf8'));
const suite=await read(directory+'/suite.json');
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1440,height:900}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.env.STUDIO_URL||'http://127.0.0.1:8765');
 await page.locator('#state[data-kind=ready]').waitFor({timeout:30000});
 let total=0;
 for(const name of suite.pilots){
  const folder=directory+'/'+name,report=await read(folder+'/pilot-report.json'),godot=await read(folder+'/godot-report.json');
  assert.equal(report.revision,suite.revision);assert.equal(godot.revision,suite.revision);
  await page.locator('#assets button').filter({hasText:report.id}).click();
  const rows=[];
  for(let level=0;level<3;level++){
   const expected=report.exports.find(r=>r.level===level&&r.path==='asset.glb');
   const path='qa-pilots/'+name+'/lod'+level+'/asset.glb';
   await page.locator('#variant').selectOption(path);
   await page.waitForFunction(p=>document.querySelector('#viewport').dataset.resource===p&&document.querySelector('#state').dataset.kind==='ready',path);
   const info=JSON.parse(await page.locator('#viewport').getAttribute('data-inspection'));
   const sha=await page.locator('#viewport').getAttribute('data-sha256');
   assert.equal(sha,expected.sha256);assert.equal(sha,godot.rows[level].sha256);
   assert.equal(info.triangles,expected.metrics.triangles);assert.equal(info.triangles,godot.rows[level].triangles);
   assert(info.normalMeshes>0&&info.uvMeshes>0);
   info.dimensions.forEach((x,i)=>assert(Math.abs(x-report.contract.dimensions_m[i])<.001));
   await page.screenshot({path:folder+'/studio-lod'+level+'.png'});
   let pose=null;
   if(expected.rig){
    const key=x=>x.toLowerCase().replace(/[:_\/ ]/g,'');
    const options=await page.locator('#node-select option').evaluateAll(o=>o.map(x=>({value:x.value,text:x.textContent})));
    const bone=options.find(o=>key(o.text).includes(key('bone'+expected.rig.pose_bone)));
    assert(bone,'authored bone must be selectable in Studio');
    await page.locator('#node-select').selectOption(bone.value);
    await page.locator('#pose-x').evaluate((el,degrees)=>{el.value=String(degrees);el.dispatchEvent(new Event('input',{bubbles:true}));},expected.rig.pose_degrees);
    await page.waitForFunction(deg=>Math.abs(JSON.parse(document.querySelector('#viewport').dataset.inspection).pose?.[0]-deg)<1,expected.rig.pose_degrees);
    await page.screenshot({path:folder+'/studio-pose-lod'+level+'.png'});
    assert(godot.rows[level].rig.child_displacement_m>.001);
    pose={bone:expected.rig.pose_bone,degrees:expected.rig.pose_degrees,godot_displacement_m:godot.rows[level].rig.child_displacement_m};
    await page.locator('#pose-reset').click();
    console.log('SUITE_STUDIO_RIG_PASS',name,level);
   }
   rows.push({level,sha256:sha,triangles:info.triangles,dimensions_m:info.dimensions,pose,visual_approval:false});
   total++;
  }
  if(process.env.REQUIRE_QA_CAPTURE==='1'){
   await page.locator('#runtime-view').selectOption('godot-lod0');
   await page.waitForFunction(()=>document.querySelector('#viewport').dataset.runtimeView==='godot-lod0');
   assert(await page.locator('#viewport img.runtime-capture').isVisible());
  }
  await writeFile(folder+'/studio-report.json',JSON.stringify({revision:report.revision,rows,visual_approval:false}));
  console.log('SUITE_STUDIO_ASSET_PASS',name,rows.length);
 }
 assert.deepEqual(errors,[]);
 console.log('SUITE_STUDIO_PASS',total);
}finally{await browser.close();}
