import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {createCameraNavigation} from './camera-navigation.js';
import {createLighting} from './lighting.js';
import {createInspection} from './inspection.js';
import {createRuntimeComposition} from './runtime-composition.js';
let compositionBuilder;
const $=id=>document.getElementById(id);
let catalog,selected,model,frame=0,request=0,renderer,scene,camera,navigation,lighting,inspection;
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
 navigation=createCameraNavigation(camera,renderer.domElement,info=>{if(info)viewport.dataset.camera=JSON.stringify(info);else delete viewport.dataset.camera;});
 lighting=await createLighting(renderer,scene);
 inspection=createInspection({scene,renderer,camera:()=>navigation.camera,viewport});
 const update=()=>{viewport.dataset.lighting=JSON.stringify(lighting.diagnostics());};
 $('grid').addEventListener('change',()=>{lighting.setGrid($('grid').checked);update();});
 $('shadows').addEventListener('change',()=>{lighting.setShadows($('shadows').checked);update();});
 $('exposure').addEventListener('input',()=>{lighting.setExposure(Number($('exposure').value));$('exposure-value').textContent=Number($('exposure').value).toFixed(2);update();});
 update();
 viewport.prepend(renderer.domElement);
 new ResizeObserver(()=>{const w=viewport.clientWidth,h=viewport.clientHeight;if(w&&h){renderer.setSize(w,h,false);navigation.resize(w,h);}}).observe(viewport);
 renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();state('Contexto WebGL perdido. Recarregue a página.','error');});
 function loop(){requestAnimationFrame(loop);navigation.update();inspection.tick();renderer.render(scene,navigation.camera);frame++;}
 loop();
}
function dispose(root){const geos=new Set(),mats=new Set(),textures=new Set();root.traverse(o=>{if(o.geometry)geos.add(o.geometry);for(const m of [].concat(o.material||[])){mats.add(m);for(const v of Object.values(m))if(v?.isTexture)textures.add(v);}if(o.isSkinnedMesh&&o.skeleton)o.skeleton.dispose();});textures.forEach(t=>t.dispose());mats.forEach(m=>m.dispose());geos.forEach(g=>g.dispose());}
function clear(){$('compare-composition').disabled=true;$('compare-composition').textContent='Comparar câmera Godot';viewport.querySelector('.composition-comparison')?.remove();delete viewport.dataset.comparison;inspection?.clear();navigation?.clear();$('view').disabled=true;$('zoom-in').disabled=true;$('zoom-out').disabled=true;lighting?.clear();$('grid-scale').textContent='—';if(lighting)viewport.dataset.lighting=JSON.stringify(lighting.diagnostics());if(model){scene.remove(model);dispose(model);model=null;}viewport.querySelectorAll('img,audio').forEach(x=>x.remove());$('reset').disabled=true;delete viewport.dataset.resource;delete viewport.dataset.sha256;delete viewport.dataset.runtimeView;delete viewport.dataset.composition;}
function fit(){if(model)navigation.reset();}
function resources(a){return [...new Set([a.preview?.resource,...(a.outputs||[]).map(x=>x.path)].filter(p=>p&&catalog.resources[p]?.status!=='missing'&&catalog.resources[p]))];}
function renderList(){const q=$('search').value.trim().toLowerCase(),cat=$('category').value;const list=catalog.assets.filter(a=>(!cat||a.category===cat)&&(!q||[a.id,a.category,a.source?.path,...resources(a)].join(' ').toLowerCase().includes(q)));$('count').textContent=list.length+' de '+catalog.assets.length+' registros';$('assets').replaceChildren(...list.map(a=>{const b=document.createElement('button');b.type='button';b.dataset.asset=a.id;b.setAttribute('aria-current',String(a===selected));b.textContent=a.id;const sm=document.createElement('small');sm.textContent=a.category+' · '+(a.runtime_views?.length?'captura Godot disponível':resources(a).length?'arquivo real':a.runtime_samples?.length&&catalog.surface_payload?'composição 3D disponível':'captura pendente');b.append(sm);b.addEventListener('click',()=>select(a));return b;}));}
function sampleDetails(){
 const id=$('runtime-sample').value,m=catalog.runtime_samples?.[id];
 $('runtime-sample-info').textContent=m?[
 'Escopo: subárvore inteira da amostra, não orçamento individual.',
 'Nós: '+m.nodes+' · malhas: '+m.mesh_nodes+' · superfícies: '+m.surfaces,
 'Vértices: '+m.vertices+' · triângulos conhecidos: '+m.triangles,
 'Superfícies sem topologia medida: '+m.unknown_triangle_surfaces,
 'Colisões ativas: '+m.enabled_colliders+' · desativadas: '+m.disabled_colliders,
 'Classes: '+JSON.stringify(m.collision_classes),
 'LOD bias: '+JSON.stringify(m.lod_bias_counts)+' · índices LOD não medidos',
 'Buffers procedurais reais: '+(m.procedural_buffer_count??'não capturados'),
 'Composição: '+(m.composition_available?'hierarquia e referências de malha registradas (inspeção de dados)':'pendente'),
 'Famílias: '+m.families.join(', ')
 ].join('\n'):'Nenhuma amostra reconciliada nesta revisão.';
}
function selectSamples(a){
 const ids=(a.runtime_samples||[]).filter(id=>catalog.runtime_samples?.[id]);
 $('runtime-sample').replaceChildren(...ids.map(id=>new Option(id,id)));
 $('runtime-sample').disabled=!ids.length;$('open-composition').disabled=!ids.length||!catalog.surface_payload;sampleDetails();
}
$('runtime-sample').addEventListener('change',sampleDetails);
$('open-composition').addEventListener('click',async()=>{
 const id=$('runtime-sample').value,token=++request;clear();details(selected,undefined);$('runtime-view').value='';$('title').textContent='Composição · '+id;
 state('Reconstruindo superfícies reais…','loading');
 $('fidelity').textContent='Composição estática · buffers reais Godot · iluminação Studio';
 try{
  compositionBuilder??=createRuntimeComposition(catalog);
  const data=await compositionBuilder(id);if(token!==request){dispose(data.scene);return;}
  const box=new THREE.Box3();data.scene.updateMatrixWorld(true);data.scene.traverseVisible(n=>{if(n.isMesh&&n.geometry.boundingBox)box.union(n.geometry.boundingBox.clone().applyMatrix4(n.matrixWorld));});if(box.isEmpty()){dispose(data.scene);throw Error('Composição sem geometria visível');}
  model=data.scene;scene.add(model);const step=lighting.place(model,box);inspection.attach(data,selected);navigation.setBounds(box);
  for(const k of ['pose-x','pose-y','pose-z','pose-reset'])$(k).disabled=true;row('Pose','Captura estática; articulação desabilitada nesta composição');
  $('grid-scale').textContent=Number(step.toPrecision(4))+' m / célula';for(const k of ['view','reset','zoom-in','zoom-out'])$(k).disabled=false;
  viewport.dataset.composition=JSON.stringify(data.stats);$('compare-composition').disabled=!(catalog.composition_views||[]).some(v=>v.sample===id);row('Amostra',id);row('Superfícies visíveis',data.stats.visibleSurfaces);row('Triângulos visíveis',data.stats.triangles);row('Limitações',data.stats.warnings.join(' · '));
  state('Composição reconstruída dos buffers Godot','ready');
 }catch(e){if(token===request){clear();state('Falha na composição: '+e.message,'error');}}
});
$('compare-composition').addEventListener('click',async()=>{
 const panel=viewport.querySelector('.composition-comparison');
 if(panel){panel.remove();delete viewport.dataset.comparison;$('compare-composition').textContent='Comparar câmera Godot';return;}
 const stats=JSON.parse(viewport.dataset.composition||'{}'),ref=catalog.composition_views?.find(v=>v.sample===stats.id),token=request;
 if(!ref||!model)return;
 let url;
 try{
  const resp=await fetch(safePath(ref.resource),{cache:'no-store'});if(!resp.ok)throw Error('HTTP '+resp.status);
  const bytes=await resp.arrayBuffer(),hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
  if(hash!==ref.sha256)throw Error('Hash da referência divergente');
  if(token!==request)return;
  const nativeCamera=new THREE.Camera();
  nativeCamera.matrixAutoUpdate=false;nativeCamera.matrix.fromArray(ref.camera_world);
  nativeCamera.updateMatrixWorld(true);nativeCamera.projectionMatrix.fromArray(ref.projection);
  nativeCamera.projectionMatrixInverse.copy(nativeCamera.projectionMatrix).invert();
  let error=0;
  for(const p of ref.landmarks){
   const v=new THREE.Vector3(...p.world).project(nativeCamera);
   error=Math.max(error,Math.abs((v.x+1)*ref.width/2-p.pixel[0]),Math.abs((1-v.y)*ref.height/2-p.pixel[1]));
  }
  if(error>1)throw Error('Projeção divergente: '+error+' px');
  const oldSize=renderer.getSize(new THREE.Vector2()),oldRatio=renderer.getPixelRatio();
  let render;
  try{
   renderer.setPixelRatio(1);renderer.setSize(ref.width,ref.height,false);
   renderer.render(scene,nativeCamera);render=renderer.domElement.toDataURL('image/png');
  }finally{renderer.setPixelRatio(oldRatio);renderer.setSize(oldSize.x,oldSize.y,false);}
  const overlay=document.createElement('div');overlay.className='composition-comparison';
  url=URL.createObjectURL(new Blob([bytes],{type:'image/png'}));
  for(const [label,src] of [['Godot — captura original, menu oculto',url],['Studio — mesma câmera, iluminação de inspeção',render]]){
   const f=document.createElement('figure'),img=document.createElement('img'),caption=document.createElement('figcaption');
   img.alt=label;img.src=src;caption.textContent=label;f.append(img,caption);overlay.append(f);
   await img.decode();
  }
  if(token!==request)return;
  viewport.append(overlay);viewport.dataset.comparison=JSON.stringify({sample:ref.sample,landmarks:ref.landmarks.length,maxProjectionErrorPx:error,width:ref.width,height:ref.height,referenceSHA256:hash});
  $('compare-composition').textContent='Voltar à composição 3D';
 }catch(e){if(token===request)state('Falha na comparação: '+e.message,'error');}
 finally{if(url)URL.revokeObjectURL(url);}
});
function details(a,p){$('details').replaceChildren();row('ID',a.id);row('Categoria',a.category);row('Uso',a.usage);row('Fonte',a.source?.path);row('Arquivo',p);row('SHA-256',catalog.resources[p]?.sha256);row('Runtime',a.validation?.runtime);row('Homologação','Não homologado');row('Procedência',a.provenance);textList($('deps'),[...new Set([...(a.dependencies?.resources||[]),...(a.dependencies?.assets||[]),...(a.dependencies?.sources||[]),...(catalog.resources[p]?.gltf_dependencies||[]).map(d=>d.path)])]);textList($('gaps'),[...(a.gaps||[]),'Prévia não certifica materiais ou poses efetivos do Godot.']);}
function select(a){selected=a;selectSamples(a);$('title').textContent=a.id;renderList();const paths=resources(a);$('variant').replaceChildren(...paths.map(p=>{const o=document.createElement('option');o.value=p;o.textContent=p.split('/').pop();return o;}));$('variant').disabled=!paths.length;
 const selector=$('runtime-view');selector.replaceChildren(new Option('Arquivo 3D / recurso',''),...(a.runtime_views||[]).map(v=>new Option(v.label,v.id)));selector.disabled=!(a.runtime_views||[]).length;selector.value='';
 load(paths.includes(a.preview?.resource)?a.preview.resource:paths[0]);}
async function verified(p){const res=await fetch(safePath(p),{cache:'no-store'});if(!res.ok)throw Error('HTTP '+res.status);const bytes=await res.arrayBuffer();const expected=catalog.resources[p].sha256;const actual=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');if(!expected||actual!==expected)throw Error('Hash divergente');return bytes;}
async function load(p){
 $('title').textContent=selected.id;$('runtime-view').value='';
 const token=++request;clear();details(selected,p);$('fidelity').textContent=p?'Arquivo original · sem substituição geométrica':'Composição real ainda não exportada';
 if(!p){state('Sem prévia 3D: dados de runtime necessários.','unavailable');return;}
 $('variant').value=p;state('Verificando arquivo…','loading');
 try{
 const bytes=await verified(p);if(token!==request)return;
 const ext=p.split('.').pop().toLowerCase();
 if(ext==='glb'||ext==='gltf'){
   // Each load uses its own manager; never modify the global loading manager.
   // Preverify external glTF resources and pass those exact bytes to the loader.
   const manager=new THREE.LoadingManager(),loader=new GLTFLoader(manager);
   const base=new URL(safePath(p),location.href).href.replace(/[^/]+$/,'');
   const dependencyURLs=new Map(),objectURLs=[];
   let data;
   try {
     for(const dep of catalog.resources[p].gltf_dependencies||[]){
       const url=new URL(dep.uri,base);
       const expectedURL=new URL(safePath(dep.path),location.href);
       if(url.origin!==expectedURL.origin||url.search||url.hash||decodeURIComponent(url.pathname)!==decodeURIComponent(expectedURL.pathname)||!catalog.resources[dep.path]||catalog.resources[dep.path].status==='missing')throw Error('Dependência não catalogada: '+dep.uri);
       const raw=await verified(dep.path);
       if(token!==request)return;
       const types={png:'image/png',jpg:'image/jpeg',jpeg:'image/jpeg',webp:'image/webp',ktx2:'image/ktx2',bin:'application/octet-stream'};
       const objectURL=URL.createObjectURL(new Blob([raw],{type:types[dep.path.split('.').pop().toLowerCase()]||'application/octet-stream'}));
       objectURLs.push(objectURL);dependencyURLs.set(url.href,objectURL);
     }
     manager.setURLModifier(url=>{
       if(url.startsWith('data:')||url.startsWith('blob:'))return url;
       const resolved=new URL(url,base).href;
       if(!dependencyURLs.has(resolved))throw Error('Dependência não verificada: '+url);
       return dependencyURLs.get(resolved);
     });
     data=await loader.parseAsync(bytes,base);
   } finally {for(const url of objectURLs)URL.revokeObjectURL(url);}
   if(token!==request){dispose(data.scene);return;}
   const box=new THREE.Box3().setFromObject(data.scene,true);if(box.isEmpty()) {dispose(data.scene);throw Error('Modelo vazio');}
   model=data.scene;scene.add(model);const step=lighting.place(model,box);inspection.attach(data,selected);$('grid-scale').textContent=Number(step.toPrecision(4))+' m / célula';viewport.dataset.lighting=JSON.stringify(lighting.diagnostics());navigation.setBounds(box);$('view').disabled=false;$('reset').disabled=false;$('zoom-in').disabled=false;$('zoom-out').disabled=false;state('Modelo original carregado','ready');
 }else if(['png','jpg','jpeg','webp'].includes(ext)){
   const img=document.createElement('img');img.alt=p;img.src=safePath(p);viewport.append(img);state('Textura original','ready');
 }else if(['ogg','wav','mp3'].includes(ext)){
   const audio=document.createElement('audio');audio.controls=true;audio.src=safePath(p);audio.style.cssText='position:absolute;left:10%;top:45%;width:80%';viewport.append(audio);state('Áudio original','ready');
 }else{state('Arquivo catalogado; visualização específica pendente.','unavailable');return;}
 viewport.dataset.resource=p;viewport.dataset.sha256=catalog.resources[p].sha256;
 }catch(e){if(token===request){clear();state('Falha: '+e.message,'error');}}
}
async function loadRuntime(id){
 if(!id){load($('variant').value||undefined);return;}
 const view=selected?.runtime_views?.find(v=>v.id===id);if(!view)return;
 const token=++request;clear();$('title').textContent=selected.id;$('runtime-view').value=id;details(selected,undefined);
 $('fidelity').textContent='Captura real do Godot · imagem estática, não modelo 3D';
 state('Verificando captura…','loading');
 try{
  if(catalog.runtime_views?.revision!==catalog.revision||view.fidelity!=='actual_godot_frame')throw Error('Captura desatualizada');
  const response=await fetch(safePath(view.resource),{cache:'no-store'});if(!response.ok)throw Error('HTTP '+response.status);
  const bytes=await response.arrayBuffer(),hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
  if(hash!==view.sha256)throw Error('Hash da captura divergente');if(token!==request)return;
  const image=new Image();image.className='runtime-capture';image.alt=view.label;
  const url=URL.createObjectURL(new Blob([bytes],{type:'image/png'}));
  try{image.src=url;await image.decode();}finally{URL.revokeObjectURL(url);}
  if(token!==request)return;
  if(image.naturalWidth!==view.width||image.naturalHeight!==view.height)throw Error('Dimensões divergentes');
  viewport.append(image);row('Captura',view.label);row('Revisão',catalog.revision);row('SHA-256 da captura',hash);row('Câmera',view.camera.path);row('Modo',view.context.kind);
  if(view.context.collision_shape_counts){row('Colisões habilitadas',view.context.enabled_colliders);row('Debug meshes reais',view.context.debug_mesh_count);row('Classes de colisão',JSON.stringify(view.context.collision_shape_counts));row('Limitação do overlay','Linhas da Shape3D, sem teste de profundidade; captura estática');}
  if(view.context.lod_bias_counts){row('LOD bias real (instâncias)',JSON.stringify(view.context.lod_bias_counts));row('Índices explícitos de LOD','Não medidos; não inferir níveis pelo bias');}
  if(view.context.native_player_tps===false)row('Limitação','Câmera externa QA de aliado, não TPS do jogador');
  viewport.dataset.runtimeView=id;viewport.dataset.sha256=hash;state('Captura original do Godot','ready');
 }catch(e){if(token===request){clear();state('Falha na captura: '+e.message,'error');}}
}
$('runtime-view').addEventListener('change',()=>loadRuntime($('runtime-view').value));
$('variant').addEventListener('change',()=>load($('variant').value));$('reset').addEventListener('click',fit);$('view').addEventListener('change',()=>{navigation.setView($('view').value);lighting.setBottomView($('view').value==='bottom');viewport.dataset.lighting=JSON.stringify(lighting.diagnostics());});$('zoom-in').addEventListener('click',()=>navigation.zoom(.8));$('zoom-out').addEventListener('click',()=>navigation.zoom(1.25));$('search').addEventListener('input',renderList);$('category').addEventListener('change',renderList);
try{
 await initRenderer();const res=await fetch('./live_catalog.json',{cache:'no-store'});if(!res.ok)throw Error('Catálogo indisponível: '+res.status);catalog=await res.json();if(catalog.kind!=='frontline_live_catalog'||catalog.schema_version!==1||!Array.isArray(catalog.assets))throw Error('Catálogo incompatível');
 $('revision').textContent='main · '+catalog.revision.slice(0,7)+' · '+catalog.assets.length+' registros';
 for(const c of [...new Set(catalog.assets.map(a=>a.category))].sort()){const o=document.createElement('option');o.value=c;o.textContent=c;$('category').append(o);}
 renderList();const initial=catalog.assets.find(a=>resources(a).some(p=>p.endsWith('.glb')));if(initial)select(initial);else state('Selecione um recurso.','unavailable');
}catch(e){state('Falha de inicialização: '+e.message,'error');}

const fullscreen=$('fullscreen'),workspace=document.querySelector('.workspace');
function fullscreenState(){const active=document.fullscreenElement===workspace;fullscreen.textContent=active?'Sair da tela cheia':'Tela cheia';fullscreen.setAttribute('aria-pressed',String(active));}
fullscreen.disabled=!document.fullscreenEnabled||!workspace.requestFullscreen;
fullscreen.addEventListener('click',async()=>{try{if(document.fullscreenElement===workspace)await document.exitFullscreen();else await workspace.requestFullscreen();}catch(e){$('fullscreen-status').textContent='Tela cheia indisponível: '+e.message;}});
document.addEventListener('fullscreenchange',()=>{fullscreenState();$('fullscreen-status').textContent='';});
