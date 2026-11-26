import {readFileSync,writeFileSync,mkdtempSync,rmSync,mkdirSync,cpSync,copyFileSync,readdirSync,lstatSync} from "node:fs";
import {resolve,dirname,join,relative,isAbsolute,sep} from "node:path";
import {fileURLToPath} from "node:url";
import {tmpdir} from "node:os";
import {createHash} from "node:crypto";
import {execFileSync} from "node:child_process";

export function collectArsenal(manifest,sources,models) {
  const require=(ok,message)=>{if(!ok)throw Error(message)};
  const same=(a,b)=>JSON.stringify([...a].sort())===JSON.stringify([...b].sort());
  const generator="tools/build_weapons.py",player="scripts/player.gd",shop="scripts/main.gd";
  const deps=[generator,player,shop,"scripts/model_surface.gd","scripts/weapon_materials.gd","tools/generate_foley_textures.py"];
  for(const p of deps)require(sources[p]&&/^[a-f0-9]{40}$/.test(sources[p].git_blob_sha1)&&typeof sources[p].text==="string","Missing source: "+p);
  const text=sources[player].text,block=text.match(/^const WEAPONS\s*:?=\s*\{([\s\S]*?)^\}/m);
  require(block,"Cannot identify WEAPONS");
  const names=[...block[1].matchAll(/^\s*"([a-z_]+)"\s*:\s*\{/gm)].map(m=>m[1]).sort();
  require(names.length>0&&new Set(names).size===names.length,"Invalid weapon IDs");
  const weapons=manifest.assets.filter(a=>a.category==="weapon"),expected=new Set(),entries=[];
  require(same(names,weapons.map(a=>a.id.slice(7))),"Weapon IDs differ from baseline");
  for(const name of names){
    const id="weapon:"+name,a=weapons.find(a=>a.id===id);
    require(a&&a.source.path===generator&&a.source.editable===true&&a.source.functions.includes(name),"Invalid source: "+id);
    require(new RegExp("^def "+name+"\\(\\):","m").test(sources[generator].text),"Missing recipe: "+name);
    require(new RegExp("\\bg\\.save\\(['\"]"+name+"['\"]\\)").test(sources[generator].text),"Missing export: "+name);
    const roles=name==="shotgun"?["merged","body","action"]:["merged","body","action","mag"];
    require(same(roles,a.outputs.map(o=>o.role)),"Variant coverage mismatch: "+name);
    const outputs=roles.map(role=>{
      const p="assets/models/"+name+(role==="merged"?"":"_"+role)+".glb";
      require(a.outputs.some(o=>o.role===role&&o.path===p)&&!expected.has(p),"Invalid/duplicate output: "+p);
      expected.add(p);
      require(/^[a-f0-9]{40}$/.test(models[p]||""),"Missing current GLB: "+p);
      return {role,path:p,git_blob_sha1:models[p],baseline_changed:models[p]!==manifest.resources[p]?.git_blob_sha1};
    });
    entries.push({id,canonical_source:{path:generator,recipe:name,git_blob_sha1:sources[generator].git_blob_sha1},outputs,validation:{reproduction:"pending",studio_visual:"pending",godot_visual:"pending",approved:false}});
  }
  const others=new Set(manifest.assets.filter(a=>a.category!=="weapon").flatMap(a=>a.outputs.map(o=>o.path)).filter(p=>p.startsWith("assets/models/")&&p.endsWith(".glb")));
  require(same(expected,Object.keys(models).filter(p=>!others.has(p))),"Unregistered or missing arsenal GLB");
  const fn=name=>{const start=text.indexOf("\nfunc "+name+"(");require(start>=0,"Missing runtime recipe: "+name);const next=text.indexOf("\nfunc ",start+1);return text.slice(start,next<0?undefined:next)};
  const install=fn("install_attachment"),build=fn("_build_attachment_models"),scope=fn("_build_sniper_scope");
  const ids=new Set([...install.matchAll(/\bid not in \[([^\]]+)\]|\bid == "([a-z0-9_]+)"/g)].flatMap(m=>m[1]?[...m[1].matchAll(/"([^"]+)"/g)].map(x=>x[1]):[m[2]]));
  const optics=["red_dot","holo","scope4","scope_2x","scope_4x"],muzzles=["suppressor","compensator"];
  require(same(ids,[...optics,...muzzles]),"Attachment guard differs: "+[...ids].sort().join(","));
  const family=manifest.assets.find(a=>a.id==="viewmodel:attachments");
  require(family?.source.path===player&&family.source.editable===true&&family.source.functions.includes("_build_attachment_models")&&family.source.functions.includes("_build_sniper_scope"),"Missing canonical attachment family");
  require(build.includes("_build_sniper_scope(")&&scope.includes("Attachment_Optic_")&&build.includes("Attachment_Muzzle_"),"Missing runtime assembly");
  const attachments=[...optics,...muzzles].sort().map(id=>{
    require(sources[shop].text.includes('"'+id+'"'),"Attachment not referenced by shop: "+id);
    return {id,slot:optics.includes(id)?"optic":"muzzle",canonical_source:{path:player,recipe:id.startsWith("scope_")?"_build_sniper_scope":"_build_attachment_models",git_blob_sha1:sources[player].git_blob_sha1},output_kind:"godot_runtime",standalone_glb:null,validation:{studio_visual:"pending",godot_visual:"pending",approved:false}};
  });
  return {schema_version:1,kind:"frontline_arsenal_source_index",source_registry:Object.fromEntries(deps.sort().map(p=>[p,{git_blob_sha1:sources[p].git_blob_sha1}])),weapons:entries,attachment_family:family.id,attachments,counts:{weapons:entries.length,glbs:expected.size,attachments:attachments.length,changed_from_baseline:entries.flatMap(a=>a.outputs).filter(o=>o.baseline_changed).length},approved:false};
}

const root=resolve(dirname(fileURLToPath(import.meta.url)),"../..");
const blob=bytes=>createHash("sha1").update("blob "+bytes.length+"\0").update(bytes).digest("hex");
const read=p=>{const f=join(root,p);if(!lstatSync(f).isFile())throw Error("Not a regular file: "+p);return readFileSync(f)};
function main(){
  const args=process.argv.slice(2);
  if(args.length!==1&&!(args.length===3&&args[1]==="--rebuild"))throw Error("Usage: node tools/asset_pipeline/arsenal_sources.mjs /tmp/arsenal.json [--rebuild python]");
  const manifest=JSON.parse(read("assets/catalog/manifest.json"));
  const paths=["tools/build_weapons.py","scripts/player.gd","scripts/main.gd","scripts/model_surface.gd","scripts/weapon_materials.gd","tools/generate_foley_textures.py"];
  const sources=Object.fromEntries(paths.map(p=>{const b=read(p);return [p,{text:b.toString("utf8"),git_blob_sha1:blob(b)}]}));
  const tracked=execFileSync("git",["ls-files","-z","--","assets/models/"],{cwd:root,encoding:"utf8"}).split("\0").filter(p=>p.endsWith(".glb"));
  const models=Object.fromEntries(tracked.map(p=>[p,blob(read(p))]));
  const report=collectArsenal(manifest,sources,models);
  report.revision=execFileSync("git",["rev-parse","HEAD"],{cwd:root,encoding:"utf8"}).trim();
  // A dirty tree must not claim provenance from HEAD. Compare actual blob IDs.
  for(const [p,h] of Object.entries({...models,...Object.fromEntries(paths.map(p=>[p,sources[p].git_blob_sha1])),"assets/catalog/manifest.json":blob(read("assets/catalog/manifest.json"))})){
    const expected=execFileSync("git",["rev-parse",report.revision+":"+p],{cwd:root,encoding:"utf8"}).trim();
    if(h!==expected)throw Error("Source/output drift from HEAD: "+p);
  }
  report.reproduction={state:"not_run"};
  if(args[1]==="--rebuild"){
    const work=mkdtempSync(join(tmpdir(),"frontline-arsenal-"));
    try{
      const rebuild=label=>{
        const dir=join(work,label);
        mkdirSync(join(dir,"tools"),{recursive:true});
        copyFileSync(join(root,"tools/build_weapons.py"),join(dir,"tools/build_weapons.py"));
        cpSync(join(root,"tools/asset_pipeline/parametric"),join(dir,"tools/asset_pipeline/parametric"),{recursive:true});
        execFileSync(args[2],[join(dir,"tools/build_weapons.py")],{cwd:dir,stdio:"inherit",timeout:180000});
        const folder=join(dir,"assets/models");
        return Object.fromEntries(readdirSync(folder).filter(p=>p.endsWith(".glb")).sort().map(p=>["assets/models/"+p,blob(readFileSync(join(folder,p)))]));
      };
      const a=rebuild("first"),b=rebuild("second");
      const expected=Object.fromEntries(report.weapons.flatMap(w=>w.outputs.map(o=>[o.path,o.git_blob_sha1])));
      const union=[...new Set([...Object.keys(a),...Object.keys(b),...Object.keys(expected)])].sort();
      const nondeterministic=union.filter(p=>a[p]!==b[p]);
      const mismatches=union.filter(p=>a[p]!==expected[p]||b[p]!==expected[p]);
      report.reproduction={state:nondeterministic.length||mismatches.length?"failed":"byte_identical",nondeterministic,mismatches};
    }finally{rmSync(work,{recursive:true,force:true})}
  }
  const out=resolve(args[0]);
  const rel=relative(root,out);
  if(!isAbsolute(rel)&&rel!==".."&&!rel.startsWith(".."+sep))throw Error("Report must be written outside the checkout");
  mkdirSync(dirname(out),{recursive:true});
  writeFileSync(out,JSON.stringify(report,null,2)+"\n");
  console.log("ARSENAL_SOURCE_INDEX",JSON.stringify(report.counts),report.reproduction.state);
  if(report.reproduction.state==="failed")process.exitCode=1;
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))main();
