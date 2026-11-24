import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {createLighting} from './lighting.js';
const $=id=>document.getElementById(id);
let catalog,selected,model,frame=0,request=0,renderer,scene,camera,controls,lighting;
const viewport=$('viewport'),status=$('state');
function state(s,kind='info'){status.textContent=s;status.dataset.kind=kind;}
function safePath(p){if(typeof p!=='string'||p.startsWith('/')||p.includes('\\')||p.includes(':')||p.split('/').some(x=>!x||x==='.'||x==='..'))throw Error('Caminho inseguro');return './'+p.split('/').map(encodeURIComponent).join('/');}
function textList(el,values){el.replaceChildren(...values.map(v=>{const li=document.createElement('li');li.textContent=String(v);return li;}));}
function row(key,value){const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=key;dd.textContent=value==null?'Não medido':String(value);$('details').append(dt,dd);}
async function initRenderer(){
 renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});
 renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
 renderer.outputColorSpace=THREE.SRGBColorSpace;
 scene=new THREE.Scene();scene.background=new THREE.Color(0x222c35);
 camera=new THREE.PerspectiveCamera(42,1,.001,1000);camera.position.set(2,1.3,2);
 controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;
 lighting=await createLighting(renderer,scene);
 const update=()=>{viewport.dataset.lighting=JSON.stringify(lighting.diagnostics());};
 $('grid').addEventListener('change',()=>{lighting.setGrid($('grid').checked);update();});
 $('shadows').addEventListener('change',()=>{lighting.setShadows($('shadows').checked);update();});
 $('exposure').addEventListener('input',()=>{lighting.setExposure(Number($('exposure').value));$('exposure-value').textContent=Number($('exposure').value).toFixed(2);update();});
 update();
 viewport.prepend(renderer.domElement);
 new ResizeObserver(()=>{const w=viewport.clientWidth,h=viewport.clientHeight;if(w&&h){renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}}).observe(viewport);
 renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();state('Contexto WebGL perdido. Recarregue a página.','error');});
 function loop(){requestAnimationFrame(loop);controls.update();renderer.render(scene,camera);frame++;}
 loop();
}
function dispose(root){const geos=new Set(),mats=new Set(),textures=new Set();root.traverse(o=>{if(o.geometry)geos.add(o.geometry);for(const m of [].concat(o.material||[])){mats.add(m);for(const v of Object.values(m))if(v?.isTexture)textures.add(v);}if(o.isSkinnedMesh&&o.skeleton)o.skeleton.dispose();});textures.forEach(t=>t.dispose());mats.forEach(m=>m.dispose());geos.forEach(g=>g.dispose());}
function clear(){lighting?.clear();$('grid-scale').textContent='—';if(lighting)viewport.dataset.lighting=JSON.stringify(lighting.diagnostics());if(model){scene.remove(model);dispose(model);model=null;}viewport.querySelectorAll('img,audio').forEach(x=>x.remove());$('reset').disabled=true;delete viewport.dataset.resource;delete viewport.dataset.sha256;}
function fit(){if(!model)return;const box=new THREE.Box3().setFromObject(model,true),size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3());const radius=Math.max(size.length()/2,.0001);const v=THREE.MathUtils.degToRad(camera.fov/2),h=Math.atan(Math.tan(v)*camera.aspect);const dist=radius/Math.sin(Math.min(v,h))*1.2;controls.target.copy(center);camera.position.copy(center).add(new THREE.Vector3(1,.65,1).normalize().multiplyScalar(dist));camera.near=Math.max(radius/10000,.000001);camera.far=Math.max(dist+radius*20,1);camera.updateProjectionMatrix();controls.update();}
function resources(a){return [...new Set([a.preview?.resource,...(a.outputs||[]).map(x=>x.path)].filter(p=>p&&catalog.resources[p]?.status!=='missing'&&catalog.resources[p]))];}
function renderList(){const q=$('search').value.trim().toLowerCase(),cat=$('category').value;const list=catalog.assets.filter(a=>(!cat||a.category===cat)&&(!q||[a.id,a.category,a.source?.path,...resources(a)].join(' ').toLowerCase().includes(q)));$('count').textContent=list.length+' de '+catalog.assets.length+' registros';$('assets').replaceChildren(...list.map(a=>{const b=document.createElement('button');b.type='button';b.dataset.asset=a.id;b.setAttribute('aria-current',String(a===selected));b.textContent=a.id;const sm=document.createElement('small');sm.textContent=a.category+' · '+(resources(a).length?'arquivo real':'captura pendente');b.append(sm);b.addEventListener('click',()=>select(a));return b;}));}
function details(a,p){$('details').replaceChildren();row('ID',a.id);row('Categoria',a.category);row('Uso',a.usage);row('Fonte',a.source?.path);row('Arquivo',p);row('SHA-256',catalog.resources[p]?.sha256);row('Runtime',a.validation?.runtime);row('Homologação','Não homologado');row('Procedência',a.provenance);textList($('deps'),[...(a.dependencies?.resources||[]),...(a.dependencies?.assets||[]),...(a.dependencies?.sources||[])]);textList($('gaps'),[...(a.gaps||[]),'Prévia não certifica materiais ou poses efetivos do Godot.']);}
function select(a){selected=a;$('title').textContent=a.id;renderList();const paths=resources(a);$('variant').replaceChildren(...paths.map(p=>{const o=document.createElement('option');o.value=p;o.textContent=p.split('/').pop();return o;}));$('variant').disabled=!paths.length;load(paths.includes(a.preview?.resource)?a.preview.resource:paths[0]);}
async function verified(p){const res=await fetch(safePath(p),{cache:'no-store'});if(!res.ok)throw Error('HTTP '+res.status);const bytes=await res.arrayBuffer();const expected=catalog.resources[p].sha256;const actual=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');if(!expected||actual!==expected)throw Error('Hash divergente');return bytes;}
async function load(p){
 const token=++request;clear();details(selected,p);$('fidelity').textContent=p?'Arquivo original · sem substituição geométrica':'Composição real ainda não exportada';
 if(!p){state('Sem prévia 3D: dados de runtime necessários.','unavailable');return;}
 $('variant').value=p;state('Verificando arquivo…','loading');
 try{
 const bytes=await verified(p);if(token!==request)return;
 const ext=p.split('.').pop().toLowerCase();
 if(ext==='glb'||ext==='gltf'){
   const loader=new GLTFLoader();
   // Only repository-local, catalogued external dependencies may load.
   loader.manager.setURLModifier(url=>{if(url.startsWith('data:')||url.startsWith('blob:'))return url;const resolved=new URL(url,location.href);if(resolved.origin!==location.origin)throw Error('Dependência externa proibida');return resolved.href;});
   const data=await loader.parseAsync(bytes,new URL(safePath(p),location.href).href.replace(/[^/]+$/,''));
   if(token!==request){dispose(data.scene);return;}
   const box=new THREE.Box3().setFromObject(data.scene,true);if(box.isEmpty()) {dispose(data.scene);throw Error('Modelo vazio');}
   model=data.scene;scene.add(model);const step=lighting.place(model,box);$('grid-scale').textContent=Number(step.toPrecision(4))+' m / célula';viewport.dataset.lighting=JSON.stringify(lighting.diagnostics());fit();$('reset').disabled=false;state('Modelo original carregado','ready');
 }else if(['png','jpg','jpeg','webp'].includes(ext)){
   const img=document.createElement('img');img.alt=p;img.src=safePath(p);viewport.append(img);state('Textura original','ready');
 }else if(['ogg','wav','mp3'].includes(ext)){
   const audio=document.createElement('audio');audio.controls=true;audio.src=safePath(p);audio.style.cssText='position:absolute;left:10%;top:45%;width:80%';viewport.append(audio);state('Áudio original','ready');
 }else{state('Arquivo catalogado; visualização específica pendente.','unavailable');return;}
 viewport.dataset.resource=p;viewport.dataset.sha256=catalog.resources[p].sha256;
 }catch(e){if(token===request){clear();state('Falha: '+e.message,'error');}}
}
$('variant').addEventListener('change',()=>load($('variant').value));$('reset').addEventListener('click',fit);$('search').addEventListener('input',renderList);$('category').addEventListener('change',renderList);
try{
 await initRenderer();const res=await fetch('./live_catalog.json',{cache:'no-store'});if(!res.ok)throw Error('Catálogo indisponível: '+res.status);catalog=await res.json();if(catalog.kind!=='frontline_live_catalog'||catalog.schema_version!==1||!Array.isArray(catalog.assets))throw Error('Catálogo incompatível');
 $('revision').textContent='main · '+catalog.revision.slice(0,7)+' · '+catalog.assets.length+' registros';
 for(const c of [...new Set(catalog.assets.map(a=>a.category))].sort()){const o=document.createElement('option');o.value=c;o.textContent=c;$('category').append(o);}
 renderList();const initial=catalog.assets.find(a=>resources(a).some(p=>p.endsWith('.glb')));if(initial)select(initial);else state('Selecione um recurso.','unavailable');
}catch(e){state('Falha de inicialização: '+e.message,'error');}
