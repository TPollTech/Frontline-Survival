import * as THREE from 'three';
const require=(ok,msg)=>{if(!ok)throw Error(msg);};
const hex=async b=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b)),x=>x.toString(16).padStart(2,'0')).join('');
const decode=s=>Uint8Array.from(atob(s),x=>x.charCodeAt(0));
async function checked(row){const b=decode(row.data);require(b.byteLength===row.bytes&&await hex(b)===row.sha256,'Buffer divergente');return b;}
async function payload(name,hash,revision){require(name&&hash,'Payload ausente');const r=await fetch('./'+name,{cache:'no-store'});require(r.ok,'HTTP '+r.status);const b=await r.arrayBuffer();require(await hex(b)===hash,'Payload divergente');const data=JSON.parse(new TextDecoder().decode(b));require(data.revision===revision,'Revisão divergente');return data;}
// Project the captured albedo texture on the same three local/world axes.
// This is an approximation of Godot's blend, not its complete material shader.
function triplanarAlbedo(material,source){
 const scale=new THREE.Vector3(...(source.uv_scale||[1,1,1]));
 const offset=new THREE.Vector3(...(source.uv_offset||[0,0,0]));
 const sharp=Math.max(.01,source.triplanar_sharpness??1);
 const world=!!source.triplanar_world;
 material.customProgramCacheKey=()=> 'frontline-runtime-triplanar-v1-'+world;
 material.onBeforeCompile=shader=>{
  shader.uniforms.fsTriScale={value:scale};shader.uniforms.fsTriOffset={value:offset};shader.uniforms.fsTriSharp={value:sharp};
  shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 fsTriPos;\nvarying vec3 fsTriNormal;')
   .replace('#include <begin_vertex>','#include <begin_vertex>\n'+(world?'fsTriPos=(modelMatrix*vec4(position,1.0)).xyz; fsTriNormal=mat3(modelMatrix)*normal;':'fsTriPos=position; fsTriNormal=normal;'));
  shader.fragmentShader=shader.fragmentShader.replace('#include <common>','#include <common>\nvarying vec3 fsTriPos;\nvarying vec3 fsTriNormal;\nuniform vec3 fsTriScale;\nuniform vec3 fsTriOffset;\nuniform float fsTriSharp;')
   .replace('#include <map_fragment>','\n#ifdef USE_MAP\nvec3 p=fsTriPos*fsTriScale+fsTriOffset;\nvec3 w=pow(max(abs(normalize(fsTriNormal)),vec3(0.00001)),vec3(fsTriSharp));\nw/=max(w.x+w.y+w.z,0.00001);\nvec4 fsAlbedo=texture2D(map,p.zy)*w.x+texture2D(map,p.xz)*w.y+texture2D(map,p.xy)*w.z;\ndiffuseColor*=fsAlbedo;\n#endif\n');
 };
}
export function createRuntimeComposition(catalog){
 let pending=null;
 const get=()=>pending??=(Promise.all([payload(catalog.composition_payload,catalog.composition_payload_sha256,catalog.revision),payload(catalog.surface_payload,catalog.surface_payload_sha256,catalog.revision)]).catch(e=>{pending=null;throw e;}));
 return async function build(id){
  const [compositions,surfaces]=await get(),sample=compositions.samples.find(s=>s.id===id),expected=surfaces.coverage.find(s=>s.id===id);
  require(sample&&expected,'Amostra indisponível');
  const root=new THREE.Group(),groups=new Map(),geometry=new Map(),materials=new Map(),textures=new Map(),warnings=new Set();
  const stats={id,nodes:sample.nodes.length,surfaces:0,visibleSurfaces:0,triangles:0,unsupported:0,skinned:0,maxMatrixError:0};
  async function texture(t,slot,mat){
   if(!t)return null;
   const id=t.studio_sha256;if(!id){warnings.add('Textura sem pixels capturados: '+t.path);return null;}
   const key=JSON.stringify([id,slot,mat.uv_scale,mat.uv_offset]);
   if(textures.has(key))return textures.get(key);
   const row=surfaces.textures[id];require(row,'Textura não catalogada');const bytes=decode(row.data);require(bytes.length===row.bytes&&await hex(bytes)===id,'Hash de textura divergente');
   const url=URL.createObjectURL(new Blob([bytes],{type:'image/png'}));
   let tex;try{tex=await new THREE.TextureLoader().loadAsync(url);}finally{URL.revokeObjectURL(url);}
   tex.colorSpace=slot==='map'?THREE.SRGBColorSpace:THREE.NoColorSpace;
   tex.flipY=false;tex.wrapS=tex.wrapT=THREE.RepeatWrapping;
   const scale=mat.uv_scale||[1,1],offset=mat.uv_offset||[0,0];tex.repeat.set(scale[0],scale[1]);tex.offset.set(offset[0],offset[1]);tex.needsUpdate=true;
   tex.name=t.path||id;textures.set(key,tex);return tex;
  }
  async function material(m,hasColor){
   const key=JSON.stringify([m,hasColor]);if(materials.has(key))return materials.get(key);
   if(m&&m.class!=='StandardMaterial3D')warnings.add('Material não reproduzido integralmente: '+m.class);
   if(m?.triplanar)warnings.add('Albedo triplanar aproximado; shader/normal triplanar do Godot não reproduzido integralmente');
   const a=m?.albedo||[.7,.7,.7,1],color=new THREE.Color().setRGB(...a.slice(0,3),THREE.SRGBColorSpace);
   const opts={color,opacity:a[3],transparent:!!m?.transparency&&m.transparency!==2,side:m?.cull_mode===2?THREE.DoubleSide:m?.cull_mode===1?THREE.BackSide:THREE.FrontSide,vertexColors:!!m?.vertex_color_as_albedo&&hasColor};
   if(m?.transparency===2)opts.alphaTest=m.alpha_scissor_threshold??.5;
   const mat=m?.shading_mode===0?new THREE.MeshBasicMaterial(opts):new THREE.MeshStandardMaterial({...opts,metalness:m?.metallic??0,roughness:m?.roughness??.8});
   mat.map=await texture(m?.albedo_texture,'map',m||{});
   if(m?.triplanar&&mat.map)triplanarAlbedo(mat,m);
   if(mat.isMeshStandardMaterial){
    mat.normalMap=m?.normal_enabled&&!m?.triplanar?await texture(m.normal_texture,'normalMap',m):null;
    mat.normalScale.set(m?.normal_scale??1,m?.normal_scale??1);
    if(m?.emission_enabled){mat.emissive.setRGB(...m.emission.slice(0,3),THREE.SRGBColorSpace);mat.emissiveIntensity=m.emission_energy??1;}
    if(m?.metallic_texture||m?.roughness_texture)warnings.add('Canais metálico/rugosidade: inspeção escalar, packing Godot pendente');
   }
   materials.set(key,mat);return mat;
  }
  async function geo(digest){
   if(geometry.has(digest))return geometry.get(digest);
   const row=surfaces.buffers[digest];require(row,'Superfície sem buffer');
   const g=new THREE.BufferGeometry();
   for(const [name,s] of Object.entries(row.attributes)){
    const b=await checked(s);
    if(name==='index'){g.setIndex(new THREE.BufferAttribute(new Uint32Array(b.buffer),1));continue;}
    if(name==='joints'||name==='weights')continue;
    const size={position:3,normal:3,uv:2,uv1:2,tangent:4,color:4}[name];require(size,'Atributo desconhecido');
    g.setAttribute(name,new THREE.BufferAttribute(new Float32Array(b.buffer),size));
   }
   // Godot front faces clockwise, Three counterclockwise.
   if(row.primitive===3){
    if(!g.index)g.setIndex(Array.from({length:g.attributes.position.count},(_,i)=>i));
    const a=g.index.array;for(let i=0;i<a.length;i+=3){const x=a[i+1];a[i+1]=a[i+2];a[i+2]=x;}
   }
   if(!g.attributes.normal&&row.primitive===3){g.computeVertexNormals();warnings.add('Normais ausentes: derivadas para inspeção');}
   g.computeBoundingBox();g.computeBoundingSphere();geometry.set(digest,g);return g;
  }
  try{
   for(const n of sample.nodes){
    const group=new THREE.Group();group.name=n.path;group.matrixAutoUpdate=false;
    const parentPath=n.path==='.'?null:n.path.includes('/')?n.path.slice(0,n.path.lastIndexOf('/')):'.';
    const parent=parentPath===null?root:groups.get(parentPath);require(parent,'Pai ausente '+n.path);
    parent.add(group);parent.updateWorldMatrix(true,false);
    if(n.world)group.matrix.copy(parent.matrixWorld).invert().multiply(new THREE.Matrix4().fromArray(n.world));
    group.visible=n.visible_in_tree!==false;groups.set(n.path,group);
    group.updateWorldMatrix(true,false);
    if(n.world)stats.maxMatrixError=Math.max(stats.maxMatrixError,...group.matrixWorld.elements.map((v,i)=>Math.abs(v-n.world[i])));
    for(const s of n.mesh?.surfaces||[]){
     stats.surfaces++;if(n.visible_in_tree)stats.visibleSurfaces++;
     const buffer=surfaces.buffers[s.studio_sha256];require(buffer,'Buffer não encontrado');
     if(buffer.primitive!==3){if(n.visible_in_tree)stats.unsupported++;continue;}
     const g=await geo(s.studio_sha256);require(g.attributes.position.count===s.vertices&&g.index.count/3===s.triangles,'Métrica diverge da engine');
     const mesh=new THREE.Mesh(g,await material(s.effective_material,!!g.attributes.color));mesh.name=n.path+'::'+s.index;group.add(mesh);
     if(n.visible_in_tree){stats.triangles+=s.triangles;if(n.mesh.has_skin){stats.skinned++;warnings.add('Malha skinned em repouso; pose da engine não aplicada');}}
    }
   }
   require(stats.surfaces===expected.surfaces&&stats.visibleSurfaces===expected.visible_surfaces&&stats.triangles===expected.visible_triangles&&stats.unsupported===expected.unsupported_visible&&stats.skinned===expected.skinned_visible,'Cobertura divergente');
   require(stats.maxMatrixError<1e-5,'Transform divergente');
   stats.warnings=[...warnings];stats.fidelity='native_surface_arrays_static';return {scene:root,animations:[],stats};
  }catch(e){geometry.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());textures.forEach(t=>t.dispose());throw e;}
 };
}
