import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

export function corners(box){
 const points=[];
 for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z])points.push(new THREE.Vector3(x,y,z));
 return points;
}
const defaultDirection=new THREE.Vector3(1,.65,1).normalize();

// Analytical perspective fit: each corner lies within padded camera frustum.
// Only camera moves; no translation, scaling or recentering of asset geometry.
export function fitDistance(box,direction,fov,aspect,padding=1.16){
 if(box.isEmpty()||!Number.isFinite(aspect)||aspect<=0||!(fov>0&&fov<180)||padding<1)throw Error('Enquadramento inválido');
 const center=box.getCenter(new THREE.Vector3());
 const radius=Math.max(box.getSize(new THREE.Vector3()).length()/2,1e-6);
 if(!Number.isFinite(radius)||!center.toArray().every(Number.isFinite))throw Error('Bounds inválidos');
 const back=direction.clone().normalize();
 const right=new THREE.Vector3().crossVectors(new THREE.Vector3(0,1,0),back).normalize();
 if(right.lengthSq()<.5)throw Error('Direção de câmera degenerada');
 const up=new THREE.Vector3().crossVectors(back,right);
 const tan=Math.tan(THREE.MathUtils.degToRad(fov/2));
 return Math.max(radius*.05,...corners(box).map(p=>{
   p.sub(center);
   return p.dot(back)+Math.max(Math.abs(p.dot(right))*padding/(tan*aspect),Math.abs(p.dot(up))*padding/tan,radius*.02);
 }));
}

export function createCameraNavigation(camera,canvas,onChange){
 let controls,box=null,home=null;
 function configure(){
   controls?.dispose();
   controls=new OrbitControls(camera,canvas);
   controls.enableDamping=true;controls.dampingFactor=.09;
   controls.enableRotate=true;controls.enableZoom=true;controls.enablePan=true;
   controls.screenSpacePanning=true;
   controls.rotateSpeed=.8;controls.zoomSpeed=1;controls.panSpeed=.85;
   controls.minPolarAngle=.02;controls.maxPolarAngle=Math.PI-.02;
   controls.enabled=!!box;
   controls.mouseButtons={LEFT:THREE.MOUSE.ROTATE,MIDDLE:THREE.MOUSE.DOLLY,RIGHT:THREE.MOUSE.PAN};
   controls.touches={ONE:THREE.TOUCH.ROTATE,TWO:THREE.TOUCH.DOLLY_PAN};
 }
 configure();
 function diagnostics(){
   if(!box||!home)return null;
   camera.updateMatrixWorld(true);
   const projected=corners(box).map(p=>p.project(camera));
   return {position:camera.position.toArray(),target:controls.target.toArray(),
      distance:camera.position.distanceTo(controls.target),minDistance:controls.minDistance,maxDistance:controls.maxDistance,
      aspect:camera.aspect,near:camera.near,far:camera.far,damping:controls.enableDamping,
      pan:controls.enablePan,zoom:controls.enableZoom,homeDistance:home.distance,
      bounds:[box.min.toArray(),box.max.toArray()],maxNdc:Math.max(...projected.map(p=>Math.max(Math.abs(p.x),Math.abs(p.y)))),
      depthInside:projected.every(p=>p.z>=-1&&p.z<=1)};
 }
 function notify(){onChange(diagnostics());}
 function reset(){
   if(!box)return;
   const center=box.getCenter(new THREE.Vector3());
   const radius=Math.max(box.getSize(new THREE.Vector3()).length()/2,1e-6);
   const distance=fitDistance(box,defaultDirection,camera.fov,camera.aspect);
   // Fresh control instance deliberately clears queued inertial input.
   configure();
   controls.target.copy(center);controls.cursor.copy(center);
   controls.maxTargetRadius=radius*4;
   controls.minDistance=Math.max(radius*.025,1e-7);
   controls.maxDistance=Math.max(distance*8,radius*20);
   camera.position.copy(center).addScaledVector(defaultDirection,distance);
   camera.near=Math.max(radius/20000,1e-8);
   camera.far=controls.maxDistance+radius*12;
   camera.zoom=1;camera.updateProjectionMatrix();
   controls.update();controls.saveState();
   home={position:camera.position.clone(),target:center.clone(),distance};
   notify();
 }
 function setBounds(value){box=value.clone();reset();}
 function clear(){box=null;home=null;configure();notify();}
 function atHome(){return home&&camera.position.distanceTo(home.position)<home.distance*1e-6&&controls.target.distanceTo(home.target)<home.distance*1e-6;}
 function resize(w,h){
   if(!(w>0&&h>0))return;
   const refit=atHome();
   camera.aspect=w/h;camera.updateProjectionMatrix();
   if(refit)reset();else notify();
 }
 function zoom(factor){
   if(!box||!Number.isFinite(factor)||factor<=0)return;
   const offset=camera.position.clone().sub(controls.target);
   const distance=THREE.MathUtils.clamp(offset.length()*factor,controls.minDistance,controls.maxDistance);
   camera.position.copy(controls.target).add(offset.setLength(distance));
   controls.update();notify();
 }
 function update(){
   const changed=controls.update();
   if(changed)notify();
 }
 return {setBounds,reset,clear,resize,zoom,update,diagnostics};
}
