import * as THREE from 'three';
import {VertexNormalsHelper} from 'three/addons/helpers/VertexNormalsHelper.js';

const slots=['map','normalMap','roughnessMap','metalnessMap','aoMap','emissiveMap','alphaMap'];
const $=id=>document.getElementById(id);
const option=(label,value)=>new Option(label,value);
const fmt=n=>Number.isFinite(n)?Number(n.toFixed(5)):'—';
const xyz=v=>v.toArray().map(fmt);
const describeTexture=t=>({name:t.name||'(sem nome)',width:t.image?.width??null,height:t.image?.height??null,colorSpace:t.colorSpace||'linear / dados',channel:t.channel??0});
function materialsOf(mesh){return Array.isArray(mesh.material)?mesh.material:[mesh.material];}
function triangleCount(g){return Math.floor((g.index?.count??g.attributes.position?.count??0)/3);}
export function measureModel(root){
 root.updateMatrixWorld(true);
 const geometries=new Set(),materials=new Set(),textures=new Set();
 let meshes=0,vertices=0,triangles=0,uniqueVertices=0,uniqueTriangles=0,slotsCount=0,uvMeshes=0,normalMeshes=0;
 root.traverse(m=>{
  if(!m.isMesh||!m.geometry?.attributes.position)return;
  const g=m.geometry,count=m.isInstancedMesh?m.count:1;
  meshes+=count;vertices+=g.attributes.position.count*count;triangles+=triangleCount(g)*count;
  if(g.attributes.uv)uvMeshes+=count;if(g.attributes.normal)normalMeshes+=count;
  if(!geometries.has(g)){geometries.add(g);uniqueVertices+=g.attributes.position.count;uniqueTriangles+=triangleCount(g);}
  for(const mat of materialsOf(m).filter(Boolean)){slotsCount+=count;materials.add(mat);for(const k of slots)if(mat[k]?.isTexture)textures.add(mat[k]);}
 });
 const box=new THREE.Box3().setFromObject(root,true);
 return {meshes,vertices,triangles,uniqueVertices,uniqueTriangles,materials:materials.size,materialSlots:slotsCount,textures:textures.size,uvMeshes,normalMeshes,dimensions:box.isEmpty()?null:xyz(box.getSize(new THREE.Vector3())),min:box.isEmpty()?null:xyz(box.min),max:box.isEmpty()?null:xyz(box.max)};
}

// Authored inspection motion around the original local joint orientation.
export function jointInspectionClip(name, joint, axis, radians){
 const values=[0,radians,0].flatMap(angle=>joint.quaternion.clone()
  .multiply(new THREE.Quaternion().setFromAxisAngle(axis,angle)).toArray());
 return new THREE.AnimationClip(name,1,[
  new THREE.QuaternionKeyframeTrack(joint.uuid+'.quaternion',[0,.5,1],values)
 ]);
}

export function createInspection({scene,renderer,camera,viewport}){
 let root=null,asset=null,baseMetrics=null,meshes=[],nodes=[],mats=[],originals=new Map(),rest=new Map(),temporary=new Set(),helpers=[],mixer=null,action=null,clips=[],playing=false,span=1;
 const clock=new THREE.Clock();let reportElapsed=0;
 const panel=$('inspection'), metrics=$('inspection-metrics'), info=$('material-info'), uv=$('uv-preview'), diagnostics=$('inspection-diagnostics');
 const controls=['inspection-mode','material-select','texture-slot','uv-channel','normals-toggle','pivots-toggle','clip-select','clip-play','clip-time','node-select','pose-x','pose-y','pose-z','pose-reset'];
 const selectedMaterial=()=>mats[Number($('material-select').value)];
 const selectedNode=()=>nodes[Number($('node-select').value)];
 function fill(id,values){$(id).replaceChildren(...values.map(([l,v])=>option(l,v)));}
 function report(){
  if(!root)return;
  const box=new THREE.Box3().setFromObject(root,true),m={...baseMetrics,dimensions:box.isEmpty()?null:xyz(box.getSize(new THREE.Vector3())),min:box.isEmpty()?null:xyz(box.min),max:box.isEmpty()?null:xyz(box.max)};
  metrics.textContent='Instâncias de malha: '+m.meshes+'\nVértices / triângulos instanciados: '+m.vertices+' / '+m.triangles+'\nVértices / triângulos únicos: '+m.uniqueVertices+' / '+m.uniqueTriangles+'\nMateriais / slots: '+m.materials+' / '+m.materialSlots+'\nTexturas: '+m.textures+'\nAABB atual (m, X × Y × Z): '+(m.dimensions?.join(' × ')??'não medido');
  diagnostics.textContent='Colisões: '+(asset?.collision==null?'não medidas — sem proxy inventado':JSON.stringify(asset.collision,null,2))+'\nLOD: '+(asset?.lods==null?'não medido — variantes não são LOD automaticamente':JSON.stringify(asset.lods,null,2));
  viewport.dataset.inspection=JSON.stringify({...m,mode:$('inspection-mode').value,helpers:helpers.length,clips:clips.length,playing,clipTime:action?.time??0,selectedNode:selectedNode()?.name??null,pose:selectedNode()?nodeAngles():null,collisionKnown:asset?.collision!=null,lodKnown:asset?.lods!=null});
 }
 // Euler is not a Vector3; its toArray includes the order string.
 function nodeAngles(){const n=selectedNode();return n?[n.rotation.x,n.rotation.y,n.rotation.z].map(v=>Math.round(THREE.MathUtils.radToDeg(v))):[0,0,0];}
 function syncPose(){const a=nodeAngles();['pose-x','pose-y','pose-z'].forEach((id,i)=>{$(id).value=a[i];$(id+'-value').textContent=a[i]+'°';});}
 function restoreMaterials(){
  for(const [m,mat] of originals)m.material=mat;
  for(const mat of temporary)mat.dispose();
  temporary.clear();
 }
 function showMaterial(){
  const m=selectedMaterial();
  if(!m){info.textContent='Nenhum material.';fill('texture-slot',[]);$('texture-slot').disabled=true;return;}
  const available=slots.filter(k=>m[k]?.isTexture);
  const previous=$('texture-slot').value;
  fill('texture-slot',available.map(k=>[k,k]));$('texture-slot').disabled=!available.length;
  if(available.includes(previous))$('texture-slot').value=previous;
  info.textContent=JSON.stringify({name:m.name||'(sem nome)',type:m.type,color:m.color?.getHexString()??null,metalness:m.metalness??null,roughness:m.roughness??null,opacity:m.opacity,transparent:m.transparent,textures:Object.fromEntries(available.map(k=>[k,describeTexture(m[k])]))},null,2);
 }
 function applyMode(){
  if(!root)return;restoreMaterials();
  const mode=$('inspection-mode').value,slot=$('texture-slot').value,chosen=selectedMaterial();
  if(mode!=='textured'){
   const copies=new Map();
   const convert=m=>{
    if(copies.has(m))return copies.get(m);
    let next;
    if(mode==='solid')next=new THREE.MeshStandardMaterial({color:0x9aabb6,roughness:.8,side:m.side});
    else if(mode==='wireframe')next=new THREE.MeshBasicMaterial({color:0x75d7ed,wireframe:true,side:THREE.DoubleSide});
    else next=new THREE.MeshBasicMaterial({color:m===chosen&&m[slot]?0xffffff:0x343c43,map:m===chosen?m[slot]??null:null,side:m.side,toneMapped:false});
    copies.set(m,next);temporary.add(next);return next;
   };
   for(const [mesh,mat] of originals)mesh.material=Array.isArray(mat)?mat.map(convert):convert(mat);
  }
  renderer.shadowMap.needsUpdate=true;report();
 }
 function drawUV(){
  const ctx=uv.getContext('2d'),w=uv.width,h=uv.height;
  ctx.clearRect(0,0,w,h);ctx.fillStyle='#111820';ctx.fillRect(0,0,w,h);
  ctx.strokeStyle='#344655';ctx.strokeRect(8,8,w-16,h-16);
  let total=0,drawn=0;const channel=$('uv-channel').value;
  ctx.strokeStyle='#6ed9ee';ctx.lineWidth=.75;ctx.beginPath();
  for(const mesh of meshes){
   const g=mesh.geometry,a=g.getAttribute(channel);if(!a)continue;
   const n=triangleCount(g);total+=n;
   const index=i=>g.index?g.index.getX(i):i;
   for(let i=0;i<n&&drawn<12000;i++){
    for(let j=0;j<3;j++){const k=index(i*3+j),x=8+a.getX(k)*(w-16),y=h-8-a.getY(k)*(h-16);if(j===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);}
    ctx.closePath();drawn++;
   }
  }
  ctx.stroke();$('uv-summary').textContent=total?drawn+' / '+total+' triângulos UV · janela 0–1':'Canal ausente no arquivo';
 }
 function clearHelpers(){for(const h of helpers){scene.remove(h);h.geometry?.dispose();if(Array.isArray(h.material))h.material.forEach(m=>m.dispose());else h.material?.dispose();}helpers=[];}
 function rebuildHelpers(){
  clearHelpers();if(!root)return;
  root.updateMatrixWorld(true);
  if($('normals-toggle').checked)for(const mesh of meshes.filter(m=>m.geometry.attributes.normal&&!m.isSkinnedMesh&&!m.isInstancedMesh&&m.geometry.attributes.position.count<=50000).slice(0,40)){
   const h=new VertexNormalsHelper(mesh,span*.025,0x45e69a);scene.add(h);helpers.push(h);
  }
  if($('pivots-toggle').checked)for(const node of nodes.slice(0,100)){
   const h=new THREE.AxesHelper(span*.07);node.getWorldPosition(h.position);node.getWorldQuaternion(h.quaternion);h.userData.pivot=node;scene.add(h);helpers.push(h);
  }
  $('helper-summary').textContent=helpers.length+' auxiliares · normais estáticas (até 40 malhas, 50 mil vértices cada); pivôs (até 100 nós). Sem normais deformadas.';
  report();
 }
 function stop(){playing=false;action?.stop();action=null;mixer?.stopAllAction();$('clip-play').textContent='Reproduzir';}
 function resetPose(){stop();for(const [n,t] of rest){n.position.copy(t.p);n.quaternion.copy(t.q);n.scale.copy(t.s);}root?.updateMatrixWorld(true);$('clip-time').value=0;syncPose();rebuildHelpers();}
 function selectClip(){
  resetPose();const i=Number($('clip-select').value);const clip=clips[i];
  $('clip-play').disabled=!clip;$('clip-time').disabled=!clip;
  if(!clip)return;
  action=mixer.clipAction(clip);action.reset().play();action.paused=true;
  $('clip-time').max=clip.duration;$('clip-time').value=0;mixer.update(0);report();
 }
 function setPose(){if(!root)return;const n=selectedNode();if(!n)return;stop();$('clip-select').value='-1';$('clip-play').disabled=true;$('clip-time').disabled=true;const a=['pose-x','pose-y','pose-z'].map(id=>THREE.MathUtils.degToRad(Number($(id).value)));n.rotation.set(...a,n.rotation.order);root.updateMatrixWorld(true);syncPose();rebuildHelpers();renderer.shadowMap.needsUpdate=true;}
 function clear(){
  stop();if(mixer&&root)mixer.uncacheRoot(root);mixer=null;
  restoreMaterials();clearHelpers();root=null;asset=null;meshes=[];nodes=[];mats=[];originals.clear();rest.clear();clips=[];
  $('screenshot-status').textContent='';panel.hidden=true;controls.forEach(id=>$(id).disabled=true);$('screenshot').disabled=true;delete viewport.dataset.inspection;
 }
 function attach(data,a){
  clear();root=data.scene;asset=a;clips=data.animations||[];root.updateMatrixWorld(true);
  baseMetrics=measureModel(root);
  span=Math.max(new THREE.Box3().setFromObject(root,true).getSize(new THREE.Vector3()).length(),.001);
  const set=new Set();
  root.traverse(n=>{nodes.push(n);rest.set(n,{p:n.position.clone(),q:n.quaternion.clone(),s:n.scale.clone()});if(n.isMesh&&n.geometry?.attributes.position){meshes.push(n);originals.set(n,n.material);for(const m of materialsOf(n).filter(Boolean))set.add(m);}});
  mats=[...set];mixer=new THREE.AnimationMixer(root);
  fill('material-select',mats.map((m,i)=>[(m.name||m.type)+' #'+(i+1),i]));
  fill('clip-select',[['Sem animação','-1'],...clips.map((c,i)=>[(c.name||'Clip '+i)+' · '+fmt(c.duration)+' s',i])]);
  fill('node-select',nodes.flatMap((n,i)=>!data.poseNodes||data.poseNodes.includes(n)?[[(n.name||n.type)+' ['+i+']',i]]:[]));
  $('inspection-mode').value='textured';$('normals-toggle').checked=false;$('pivots-toggle').checked=false;
  controls.forEach(id=>$(id).disabled=false);$('material-select').disabled=!mats.length;$('clip-play').disabled=true;$('clip-time').disabled=true;$('screenshot').disabled=false;panel.hidden=false;
  showMaterial();drawUV();syncPose();rebuildHelpers();
 }
 function tick(){
  const delta=Math.min(clock.getDelta(),.1);
  if(!root||!playing||!action)return;
  mixer.update(delta);$('clip-time').value=action.time;root.updateMatrixWorld(true);
  for(const h of helpers){if(h.userData.pivot){h.userData.pivot.getWorldPosition(h.position);h.userData.pivot.getWorldQuaternion(h.quaternion);}else h.update?.();}
  renderer.shadowMap.needsUpdate=true;reportElapsed+=delta;if(reportElapsed>=.12){reportElapsed=0;report();}
 }
 $('inspection-mode').addEventListener('change',applyMode);
 $('material-select').addEventListener('change',()=>{showMaterial();applyMode();});
 $('texture-slot').addEventListener('change',applyMode);
 $('uv-channel').addEventListener('change',drawUV);
 for(const id of ['normals-toggle','pivots-toggle'])$(id).addEventListener('change',rebuildHelpers);
 $('clip-select').addEventListener('change',selectClip);
 $('clip-play').addEventListener('click',()=>{if(!action)return;playing=!playing;action.paused=!playing;$('clip-play').textContent=playing?'Pausar':'Reproduzir';report();});
 $('clip-time').addEventListener('input',()=>{if(!action)return;playing=false;action.paused=false;action.time=Number($('clip-time').value);mixer.update(0);action.paused=true;$('clip-play').textContent='Reproduzir';root.updateMatrixWorld(true);syncPose();rebuildHelpers();renderer.shadowMap.needsUpdate=true;});
 $('node-select').addEventListener('change',()=>{syncPose();report();});
 for(const id of ['pose-x','pose-y','pose-z'])$(id).addEventListener('input',setPose);
 $('pose-reset').addEventListener('click',()=>{$('clip-select').value='-1';resetPose();$('clip-play').disabled=true;$('clip-time').disabled=true;renderer.shadowMap.needsUpdate=true;});
 $('screenshot').addEventListener('click',()=>{
  if(!root)return;renderer.render(scene,camera());
  renderer.domElement.toBlob(blob=>{
   if(!blob){$('screenshot-status').textContent='Falha ao gerar PNG';return;}
   const link=document.createElement('a'),url=URL.createObjectURL(blob);link.href=url;link.download='frontline-'+(asset?.id||'asset').replace(/[^a-zA-Z0-9_-]/g,'-')+'.png';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);$('screenshot-status').textContent='PNG gerado';
  },'image/png');
 });
 clear();
 return {attach,clear,tick,refreshGeometry(){baseMetrics=measureModel(root);drawUV();rebuildHelpers();}};
}
