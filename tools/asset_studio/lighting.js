import * as THREE from 'three';
import {RGBELoader} from 'three/addons/loaders/RGBELoader.js';

export async function createLighting(renderer,scene){
 renderer.outputColorSpace=THREE.SRGBColorSpace;
 renderer.toneMapping=THREE.ACESFilmicToneMapping;
 renderer.toneMappingExposure=1;
 renderer.shadowMap.enabled=true;
 renderer.shadowMap.type=THREE.PCFSoftShadowMap;
 renderer.shadowMap.autoUpdate=false;
 const meta=await fetch('./studio-light.json').then(r=>{if(!r.ok)throw Error('Metadados HDRI indisponíveis');return r.json();});
 const bytes=await fetch('./studio-light.hdr').then(r=>{if(!r.ok)throw Error('HDRI indisponível');return r.arrayBuffer();});
 const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
 if(hash!==meta.sha256)throw Error('Hash HDRI divergente');
 const decoded=new RGBELoader().parse(bytes);
 if(!decoded||decoded.width!==meta.width||decoded.height!==meta.height)throw Error('HDRI inválido');
 const hdr=new THREE.DataTexture(decoded.data,decoded.width,decoded.height,THREE.RGBAFormat,decoded.type);
 hdr.colorSpace=THREE.LinearSRGBColorSpace;
 hdr.mapping=THREE.EquirectangularReflectionMapping;
 hdr.minFilter=THREE.LinearFilter;hdr.magFilter=THREE.LinearFilter;
 hdr.flipY=true;hdr.needsUpdate=true;
 const pmrem=new THREE.PMREMGenerator(renderer);
 const environment=pmrem.fromEquirectangular(hdr);
 scene.environment=environment.texture;scene.environmentIntensity=0.9;
 hdr.dispose();pmrem.dispose();
 const key=new THREE.DirectionalLight(0xfff3df,2.1);
 key.castShadow=true;key.shadow.mapSize.set(1024,1024);
 key.shadow.bias=-0.0001;key.shadow.radius=2;
 scene.add(key,key.target);
 const floor=new THREE.Mesh(new THREE.PlaneGeometry(1,1),new THREE.MeshStandardMaterial({color:0x4b535a,roughness:0.95,metalness:0}));
 floor.rotation.x=-Math.PI/2;floor.receiveShadow=true;floor.visible=false;scene.add(floor);
 let grid=null,active=false,gridEnabled=true,shadowsEnabled=true;
 function refresh(){renderer.shadowMap.needsUpdate=true;}
 function applyVisibility(){floor.visible=active;if(grid)grid.visible=active&&gridEnabled;key.castShadow=shadowsEnabled;refresh();}
 function place(model,box){
   const size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3());
   const span=Math.max(size.x,size.y,size.z,.0001);
   // Grid step in canonical metres, selecting 1/2/5×10^n.
   const wanted=span/8,base=10**Math.floor(Math.log10(wanted)),step=[1,2,5,10].map(x=>x*base).find(x=>x>=wanted);
   const cells=24,extent=cells*step;
   const y=box.min.y-span*.012;
   floor.scale.set(extent*2,extent*2,1);floor.position.set(center.x,y,center.z);
   if(grid){scene.remove(grid);grid.geometry.dispose();grid.material.dispose();}
   grid=new THREE.GridHelper(extent,cells,0x8495a0,0x65717b);
   grid.position.set(center.x,y+span*.0005,center.z);grid.material.transparent=true;grid.material.opacity=.58;scene.add(grid);
   key.target.position.copy(center);
   key.position.copy(center).add(new THREE.Vector3(1,2,1.2).normalize().multiplyScalar(span*3));
   key.target.updateMatrixWorld();
   const c=key.shadow.camera;c.left=-span*1.6;c.right=span*1.6;c.top=span*1.6;c.bottom=-span*1.6;c.near=span*.01;c.far=span*8;c.updateProjectionMatrix();
   key.shadow.normalBias=span*.002;
   model.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}});
   active=true;applyVisibility();
   return step;
 }
 function clear(){active=false;applyVisibility();}
 function setGrid(on){gridEnabled=on;applyVisibility();}
 function setShadows(on){shadowsEnabled=on;renderer.shadowMap.enabled=on;applyVisibility();}
 function setExposure(value){renderer.toneMappingExposure=value;}
 function diagnostics(){return {hdr:hash,environment:!!scene.environment,aces:renderer.toneMapping===THREE.ACESFilmicToneMapping,srgb:renderer.outputColorSpace===THREE.SRGBColorSpace,antialias:renderer.getContext().getContextAttributes().antialias,softShadow:renderer.shadowMap.type===THREE.PCFSoftShadowMap,shadows:renderer.shadowMap.enabled,grid:!!grid?.visible,floor:floor.visible,exposure:renderer.toneMappingExposure};}
 return {place,clear,setGrid,setShadows,setExposure,diagnostics};
}
