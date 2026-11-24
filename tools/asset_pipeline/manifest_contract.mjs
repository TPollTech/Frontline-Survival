function invariant(condition,message){if(!condition)throw Error(message);}

function canonicalJSON(value){function sort(x){if(Array.isArray(x))return x.map(sort);if(x!==null&&typeof x==="object")return Object.fromEntries(Object.keys(x).sort().map(k=>[k,sort(x[k])]));return x;}return JSON.stringify(sort(value),null,2)+"\n";}

function blenderToCanonical(v){invariant(Array.isArray(v)&&v.length===3&&v.every(Number.isFinite),"invalid Blender vector");return [v[0],v[2],-v[1]].map(x=>Object.is(x,-0)?0:x);}

function canonicalToBlender(v){invariant(Array.isArray(v)&&v.length===3&&v.every(Number.isFinite),"invalid canonical vector");return [v[0],-v[2],v[1]].map(x=>Object.is(x,-0)?0:x);}

function buildManifest(inv){
 const sort=(a,b)=>a<b?-1:a>b?1:0;
 const files=[...inv.files].sort((a,b)=>sort(a.path,b.path));
 const resources=Object.fromEntries(files.map(f=>[f.path,{category:f.category,bytes:f.bytes,git_blob_sha1:f.git_blob_sha1,consumers:f.consumers,usage:f.status,provenance:f.license,source_hint:f.source}]));
 const registry=Object.fromEntries([...inv.source_scripts,...inv.tooling,...inv.scenes].sort((a,b)=>sort(a.path,b.path)).map(f=>[f.path,{git_blob_sha1:f.git_blob_sha1}]));
 const source=(path,kind,functions=[],editable=true)=>({path,kind,functions,editable,git_blob_sha1:registry[path]?.git_blob_sha1??resources[path]?.git_blob_sha1??null});
 const entry=(id,category,usage,src,outputs,preview,extras={})=>({id,category,usage,source:src,outputs,preview,dependencies:{resources:[],assets:[],sources:[]},coordinates:{unit:category==="audio"||category==="texture"?"not_spatial":"m",up:category==="audio"||category==="texture"?null:"+Y",forward:category==="weapon"?"-Z":null},dimensions_m:null,bounds_m:null,pivots:null,hierarchy:null,animations:null,collision:null,lods:null,materials:null,budget:null,provenance:null,validation:{static:"inventory_only",runtime:"pending",studio_visual:"pending",godot_visual:"pending",evidence:[],approved:false},gaps:[],...extras});
 const out=(f,role)=>({path:f.path,role});
 const weapons=[...new Set(files.filter(f=>f.category==="weapon_mesh").map(f=>f.asset_id))].sort(sort);
 const assets=[];
 const textures=files.filter(f=>f.category==="texture"&&f.path.includes("/weapon_")).map(f=>f.path);
 for(const id of weapons){const f=files.filter(f=>f.asset_id===id);const a=f[0];assets.push(entry(id,"weapon","legacy_active",source(a.source,"python_recipe",[a.source_function]),f.map(x=>out(x,x.variant)),{mode:"glb_and_runtime_composition",resource:f.find(x=>x.variant==="merged").path,composition_asset:"viewmodel:assembly",fidelity:"raw_glb_only_until_runtime_capture"},{dependencies:{resources:textures,assets:["material:weapon_overrides","viewmodel:hands","viewmodel:attachments"],sources:["scripts/player.gd","scripts/enemy.gd","scripts/ally.gd","scripts/weapon_materials.gd"]},materials:{effective_source:"scripts/weapon_materials.gd",texture_paths:textures,mode:"godot_override_pending_capture"},provenance:a.license,gaps:[...a.gaps,"dimensions, pivots, hierarchy, animation and LOD not measured"]}));}
 for(const f of files.filter(x=>x.category==="character_mesh"))assets.push(entry("character:quaternius_base_male","character","experimental_disabled",source(f.path,"imported_binary",[],false),[out(f,"imported")],{mode:"glb_and_runtime_composition",resource:f.path,composition_asset:"character:quaternius_equipment",fidelity:"raw_glb_only_until_runtime_capture"},{dependencies:{resources:[],assets:["character:quaternius_equipment"],sources:["scripts/quaternius_soldier_visual.gd"]},provenance:f.license,gaps:f.gaps}));
 for(const f of files.filter(x=>["texture","audio"].includes(x.category))){const generated=f.source.startsWith("tools/");const id=f.category+":"+f.path.slice("assets/".length).replace(/\.[^.]+$/,"");assets.push(entry(id,f.category,"legacy_referenced",source(generated?f.source:f.path,generated?"python_recipe":"imported_binary",[],generated),[out(f,"resource")],{mode:"resource_inspection",resource:f.path,fidelity:"original_file"},{provenance:f.license,gaps:f.gaps,validation:{static:"inventory_only",runtime:"pending",studio_visual:"not_applicable",godot_visual:"not_applicable",evidence:[],approved:false}}));}
 for(const f of inv.runtime_families){const dep={resources:[],assets:[],sources:[]};if(f.id==="map:campo_de_testes"){dep.resources=["assets/textures/asphalt.png","assets/textures/depot_concrete.png"];dep.assets=["environment:lighting","geometry:model_surface"];dep.sources=["scenes/main.tscn","scripts/model_surface.gd"];}if(f.id==="viewmodel:assembly"){dep.assets=[...weapons,"viewmodel:hands","viewmodel:attachments","effect:muzzle","effect:scope_overlay","material:weapon_overrides"];dep.sources=["scripts/weapon_pose.gd","scripts/weapon_materials.gd","scripts/model_surface.gd"];}if(f.id==="material:weapon_overrides")dep.resources=textures;if(["enemy:legacy","ally:legacy","object:loot"].includes(f.id)){dep.assets=["geometry:model_surface","material:weapon_overrides"];dep.resources=files.filter(x=>x.category==="weapon_mesh"&&x.variant==="merged").map(x=>x.path);}if(f.id==="character:quaternius_equipment")dep.resources=files.filter(x=>x.category==="character_mesh").map(x=>x.path);
 const mode=["physics_query","collision"].includes(f.category)?"runtime_debug":f.category==="shader"?"engine_evidence":f.category==="geometry_library"||f.category==="material"?"library_inspection":"runtime_capture";
 assets.push(entry(f.id,f.category,f.status,source(f.source,"godot_recipe",f.functions),[],{mode,resource:null,fidelity:"pending_capture"},{dependencies:dep,provenance:f.license,gaps:["no live engine capture","effective transforms/materials/geometry not measured"],description:f.description}));}
 return {schema_version:1,kind:"frontline_asset_manifest",baseline_commit:inv.baseline_commit,baseline_tree:inv.baseline_tree,coverage:"static_baseline_only",coordinate_system:{handedness:"right",unit:"m",up:"+Y",right:"+X",camera_forward:"-Z",angle:"rad",quaternion_order:"xyzw",matrix_layout:"column_major",matrix_composition:"parent_world * local",blender_authoring:{up:"+Z",forward:"+Y",conversion:"[x,z,-y]"},gltf:"preserve imported basis; category front explicit; no blanket rotation"},resources,source_registry:registry,assets:assets.sort((a,b)=>sort(a.id,b.id)),dependencies:inv.dependencies,known_dynamic_gaps:inv.dynamic_expansions.filter(x=>x.absent.length).map(x=>({source:x.source,pattern:x.target,absent:x.absent,note:x.note})),migration:{mode:"additive",runtime_capture:"pending",visual_approval:"none",baseline_is_not_live_catalog:true}};
}

function validateManifest(m,inv){
 const pathOk=p=>typeof p==="string"&&p.length>0&&!p.startsWith("/")&&!p.includes("\\")&&!p.includes(":")&&!p.split("/").some(s=>!s||s==="."||s==="..");
 const hashOk=h=>typeof h==="string"&&/^[0-9a-f]{40}$/.test(h);
 invariant(m.schema_version===1&&m.kind==="frontline_asset_manifest","unsupported manifest");
 invariant(m.coverage==="static_baseline_only"&&m.migration.baseline_is_not_live_catalog===true,"baseline cannot claim live coverage");
 invariant(m.baseline_commit===inv.baseline_commit&&m.baseline_tree===inv.baseline_tree,"baseline mismatch");
 invariant(m.coordinate_system.handedness==="right"&&m.coordinate_system.unit==="m"&&m.coordinate_system.up==="+Y"&&m.coordinate_system.right==="+X"&&m.coordinate_system.camera_forward==="-Z"&&m.coordinate_system.angle==="rad"&&m.coordinate_system.quaternion_order==="xyzw"&&m.coordinate_system.matrix_layout==="column_major"&&m.coordinate_system.matrix_composition==="parent_world * local"&&m.coordinate_system.blender_authoring.conversion==="[x,z,-y]","coordinate contract mismatch");
 const records=new Map(inv.files.map(f=>[f.path,f]));
 invariant(Object.keys(m.resources).length===records.size,"resource coverage");
 for(const [path,r] of Object.entries(m.resources)){const f=records.get(path);invariant(pathOk(path)&&f&&hashOk(r.git_blob_sha1)&&r.git_blob_sha1===f.git_blob_sha1&&r.bytes===f.bytes&&r.category===f.category,"bad resource "+path);}
 const registry=new Map([...inv.source_scripts,...inv.tooling,...inv.scenes].map(f=>[f.path,f]));
 invariant(Object.keys(m.source_registry).length===registry.size,"source coverage");
 for(const [path,s] of Object.entries(m.source_registry))invariant(pathOk(path)&&hashOk(s.git_blob_sha1)&&s.git_blob_sha1===registry.get(path)?.git_blob_sha1,"bad source "+path);
 const ids=new Set(m.assets.map(a=>a.id));invariant(ids.size===m.assets.length,"duplicate asset ID");
 const expectedIds=new Set([...inv.runtime_families.map(f=>f.id),...inv.files.filter(f=>f.category==="weapon_mesh").map(f=>f.asset_id),"character:quaternius_base_male",...inv.files.filter(f=>["texture","audio"].includes(f.category)).map(f=>f.category+":"+f.path.slice("assets/".length).replace(/\.[^.]+$/,""))]);
 invariant(ids.size===expectedIds.size&&[...expectedIds].every(id=>ids.has(id)),"logical coverage mismatch");
 const owners=new Map();
 for(const a of m.assets){
  invariant(/^[a-z][a-z0-9_]*:[a-z0-9_/-]+$/.test(a.id),"invalid asset ID");
  invariant(typeof a.category==="string"&&typeof a.usage==="string"&&a.source&&pathOk(a.source.path),"invalid asset source");
  invariant(["python_recipe","godot_recipe","imported_binary"].includes(a.source.kind)&&Array.isArray(a.source.functions)&&typeof a.source.editable==="boolean","invalid source kind");
  invariant((a.source.kind==="imported_binary")===!a.source.editable,"editable source classification mismatch");
  const hash=m.source_registry[a.source.path]?.git_blob_sha1??m.resources[a.source.path]?.git_blob_sha1;
  invariant(hashOk(hash)&&a.source.git_blob_sha1===hash,"source hash mismatch "+a.id);
  invariant(Array.isArray(a.outputs)&&Array.isArray(a.gaps)&&a.gaps.length>0,"missing gaps/outputs");
  for(const o of a.outputs){invariant(pathOk(o.path)&&m.resources[o.path]&&m.resources[o.path].category!=="import_metadata"&&typeof o.role==="string","unknown output "+o.path);invariant(!owners.has(o.path),"duplicate output "+o.path);owners.set(o.path,a.id);}
  for(const p of a.dependencies.resources)invariant(pathOk(p)&&m.resources[p],"unknown resource dependency "+p);
  for(const p of a.dependencies.sources)invariant(pathOk(p)&&m.source_registry[p],"unknown source dependency "+p);
  for(const id of a.dependencies.assets)invariant(ids.has(id)&&id!==a.id,"unknown/self asset dependency "+id);
  invariant(["glb_and_runtime_composition","resource_inspection","runtime_debug","engine_evidence","library_inspection","runtime_capture"].includes(a.preview.mode),"invalid preview mode");
  if(a.preview.resource!==null)invariant(a.outputs.some(o=>o.path===a.preview.resource),"preview must use owned output");
  if(a.preview.composition_asset)invariant(ids.has(a.preview.composition_asset),"unknown composition");
  if(a.preview.mode==="glb_and_runtime_composition")invariant(a.preview.resource?.endsWith(".glb")&&a.preview.fidelity==="raw_glb_only_until_runtime_capture"&&a.preview.composition_asset,"GLB fidelity claim invalid");
  if(a.source.kind==="godot_recipe")invariant(a.outputs.length===0&&a.preview.resource===null&&a.preview.fidelity==="pending_capture","runtime preview cannot invent export");
  const v=a.validation;invariant(v.static==="inventory_only"&&v.runtime==="pending"&&["pending","not_applicable"].includes(v.studio_visual)&&["pending","not_applicable"].includes(v.godot_visual)&&v.approved===false&&Array.isArray(v.evidence)&&v.evidence.length===0,"unverified approval "+a.id);
  invariant(a.coordinates.unit===(["audio","texture"].includes(a.category)?"not_spatial":"m")&&a.coordinates.up===(["audio","texture"].includes(a.category)?null:"+Y")&&a.coordinates.forward===(a.category==="weapon"?"-Z":null),"asset coordinate mismatch");
  for(const k of ["dimensions_m","bounds_m","pivots","hierarchy","animations","collision","lods","budget"])invariant(a[k]===null,"baseline field must be unknown: "+k);
 }
 invariant([...records.values()].every(f=>f.category==="import_metadata"?!owners.has(f.path):owners.has(f.path)),"output coverage mismatch");
 for(const f of inv.runtime_families){const a=m.assets.find(a=>a.id===f.id);invariant(a.source.path===f.source&&JSON.stringify(a.source.functions)===JSON.stringify(f.functions)&&a.source.kind==="godot_recipe","runtime family source mismatch "+f.id);}
 return {assets:m.assets.length,resources:records.size,owned_outputs:owners.size,runtime_families:inv.runtime_families.length};
}

function runContractTests(inv){
 const result=[];const ok=(name,fn)=>{fn();result.push(name);};const reject=(name,mutate)=>ok(name,()=>{const m=buildManifest(inv);mutate(m);let failed=false;try{validateManifest(m,inv)}catch(e){failed=true;}invariant(failed,"accepted invalid input: "+name);});
 ok("valid manifest and baseline coverage",()=>{const r=validateManifest(buildManifest(inv),inv);invariant(r.resources===60&&r.assets===50&&r.owned_outputs===49&&r.runtime_families===24,"count mismatch");});
 ok("deterministic serialization",()=>invariant(canonicalJSON(buildManifest(inv))===canonicalJSON(buildManifest(inv)),"non-determinism"));
 ok("order-independent resource and asset inputs",()=>{const shuffled={...inv,files:[...inv.files].reverse(),runtime_families:[...inv.runtime_families].reverse()};invariant(canonicalJSON(buildManifest(inv))===canonicalJSON(buildManifest(shuffled)),"order-dependent");});
 ok("Blender basis maps right/up/forward",()=>{invariant(JSON.stringify(blenderToCanonical([1,0,0]))==="[1,0,0]"&&JSON.stringify(blenderToCanonical([0,0,1]))==="[0,1,0]"&&JSON.stringify(blenderToCanonical([0,1,0]))==="[0,0,-1]","basis mismatch");});
 ok("coordinate round trip and metric preservation",()=>{const v=[1.25,-2.5,3.75],w=blenderToCanonical(v);invariant(JSON.stringify(canonicalToBlender(w))===JSON.stringify(v)&&Math.hypot(...v)===Math.hypot(...w),"round trip");});
 ok("proper rotation not reflection",()=>{const x=blenderToCanonical([1,0,0]),y=blenderToCanonical([0,1,0]),z=blenderToCanonical([0,0,1]);const cross=[x[1]*y[2]-x[2]*y[1],x[2]*y[0]-x[0]*y[2],x[0]*y[1]-x[1]*y[0]];invariant(cross.reduce((n,v,i)=>n+v*z[i],0)===1,"reflection");});
 reject("missing resource",m=>delete m.resources[Object.keys(m.resources)[0]]);
 reject("tampered hash",m=>m.resources[Object.keys(m.resources)[0]].git_blob_sha1="0".repeat(40));
 reject("duplicate ID",m=>m.assets.push(m.assets[0]));
 reject("missing runtime family",m=>m.assets=m.assets.filter(a=>a.id!=="camera:briefing"));
 reject("unknown dependency",m=>m.assets[0].dependencies.assets.push("missing:asset"));
 reject("path traversal",m=>m.assets[0].source.path="../outside");
 reject("invented export",m=>m.assets.find(a=>a.id==="map:campo_de_testes").outputs.push({path:"assets/models/fake.glb",role:"fake"}));
 reject("raw GLB misrepresented as approved preview",m=>m.assets.find(a=>a.category==="weapon").preview.fidelity="game_exact");
 reject("false approval",m=>m.assets[0].validation.approved=true);
 reject("invented dimensions",m=>m.assets.find(a=>a.category==="weapon").dimensions_m=[1,2,3]);
 reject("wrong unit",m=>m.coordinate_system.unit="cm");
 reject("wrong source hash",m=>m.assets[0].source.git_blob_sha1="0".repeat(40));
 return result;
}

export { canonicalJSON, blenderToCanonical, canonicalToBlender, buildManifest, validateManifest, runContractTests };
