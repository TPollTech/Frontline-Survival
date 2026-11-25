"""Run existing phase-00 QA, preserve evidence and never grant visual approval."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
import zipfile

ERROR = re.compile(r'SCRIPT ERROR:|Parse Error|ASSET_RUNTIME_(?:ERROR|FAIL)|RUNTIME_VIEW_FAIL|WORLD_LOD_(?:BENCH_|MOTION_)?FAIL|IMPORT_VALIDATION_FAIL|PILOT_GODOT_FAIL|SUITE_GODOT_FAIL|EXPORT_QA_FAIL|Texture with GL ID of [0-9]+: leaked')
IDS = ('00-10','00-13','00-17','00-18','00-19','00-20','00-21','00-24','00-25','00-27','00-28','00-29','00-30','00-31','00-32','00-34')

class QA:
    def __init__(self, root, out):
        self.root, self.out = root, out
        out.mkdir(parents=True)
        self.rows = []
    def step(self, name, args, ids, *, needs=(), cwd=None, env=None, marker=None, timeout=900, engine=False):
        log = self.out / (name + '.log')
        row = {'name':name,'tasks':list(ids),'command':[str(x) for x in args],'status':'blocked','log':log.name}
        missing = [x for x in needs if not any(r['name']==x and r['status']=='passed' for r in self.rows)]
        if missing:
            log.write_text('Blocked by: '+', '.join(missing), encoding='utf-8')
        else:
            print('==', name, flush=True)
            try:
                with log.open('wb') as f:
                    p = subprocess.run([str(x) for x in args], cwd=cwd or self.root, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=timeout)
                data = log.read_text(encoding='utf-8',errors='replace')
                row['returncode'] = p.returncode
                row['status'] = 'passed' if p.returncode==0 and (marker is None or marker in data) and 'Ran 0 tests' not in data and (not engine or not ERROR.search(data)) else 'failed'
            except (OSError, subprocess.SubprocessError) as exc:
                with log.open('a',encoding='utf-8') as f: f.write('\n'+str(exc))
                row['status']='failed'
        self.rows.append(row)
        print(name, row['status'], flush=True)
        return row['status']=='passed'
    def finish(self, revision, error=None):
        summary={'revision':revision,'steps':self.rows,'fatal':error,'visual_reviewed':False,'hardware_validated':False,'homologated':False,'tasks':{i:{'steps':[r['name'] for r in self.rows if i in r['tasks']],'status':'requires_review'} for i in IDS}}
        (self.out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        files=[p for p in self.out.rglob('*') if p.is_file() and 'profile' not in p.relative_to(self.out).parts]
        hashes={}
        for p in files:
            with p.open('rb') as f: hashes[p.relative_to(self.out).as_posix()]=hashlib.file_digest(f,'sha256').hexdigest()
        (self.out/'sha256.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
        target=self.out.with_suffix('.zip')
        with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
            for p in files+[self.out/'sha256.json']: z.write(p,p.relative_to(self.out))
        with zipfile.ZipFile(target) as z:
            if z.testzip() is not None: raise RuntimeError('evidence ZIP corrupted')
        print('EVIDENCE ZIP:',target,flush=True)
        return 1 if error or any(r['status'] not in ('passed','previous_evidence_only') for r in self.rows) else 0

def run(q, rev, godot, node, npm, work, previous=None):
    py=sys.executable; root=q.root; out=q.out
    env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'; env['GITHUB_SHA']=rev
    env['FRONTLINE_REQUIRE_BLENDER']='1'
    env['PATH']=str(Path(py).parent)+os.pathsep+env['PATH']
    env.setdefault('PLAYWRIGHT_BROWSERS_PATH',str(work/'browsers'))
    def step(name,args,ids=IDS,**kw):
        kw.setdefault('env',env); return q.step(name,args,ids,**kw)
    for mode in ('lod','benchmark','motion'):
        if previous and any(r['name']==mode and r['status']=='passed' for r in previous['steps']):
            log=q.out/(mode+'.log')
            log.write_text('Prior evidence only; not executed on this revision. See original evidence '+previous['revision'],encoding='utf-8')
            q.rows.append({'name':mode,'tasks':['00-10','00-19','00-25','00-34'],'status':'previous_evidence_only','previous_revision':previous['revision'],'previous_summary_sha256':previous['summary_sha256'],'log':log.name})
            print(mode,'previous_evidence_only',flush=True)
            continue
        step(mode,[py,'tools/asset_pipeline/world_lod_local.py',out/mode,'--godot',godot]+([] if mode=='lod' else ['--'+mode]),('00-10','00-19','00-25','00-34'),timeout=1800)
    step('manifest',[node,'tools/asset_pipeline/build_manifest.mjs'])
    for label,pattern in [('windows_contract','test_qa_windows_contract.py'),('parametric','test_parametric*.py'),('gltf','test_validate_gltf.py'),('catalog','test_live_catalog.py'),('scopes','test_runtime_asset_scopes.py'),('lod_contracts','test_world_lod*.py'),('pilot_finish','test_pilot_finish.py'),('pilot_art','test_pilot_art.py'),('pilot_anatomy','test_pilot_anatomy.py'),('glove','test_continuous_glove.py'),('character','test_continuous_character.py')]:
        step(label,[py,'-m','unittest','discover','-s','tests','-p',pattern,'-v'])
    step('arsenal_tests',[node,'--test','tests/test_arsenal_sources.mjs'],('00-28','00-34'))
    step('arsenal_rebuild',[node,'tools/asset_pipeline/arsenal_sources.mjs',out/'arsenal.json','--rebuild',py],('00-28','00-34'),timeout=1800)
    for label,module in [('fixture','export_fixture'),('pilot','pilot_object'),('suite','pilot_suite')]:
        dest=out/label
        step(label,[py,'-m','tools.asset_pipeline.parametric.'+module,dest,rev],('00-21','00-24','00-25','00-27','00-34'),timeout=1800)
        repeat=work/(label+'-repeat')
        if step(label+'_repeat',[py,'-m','tools.asset_pipeline.parametric.'+module,repeat,rev],needs=(label,)):
            a={p.relative_to(dest):hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.rglob('*') if p.is_file()}
            b={p.relative_to(repeat):hashlib.sha256(p.read_bytes()).hexdigest() for p in repeat.rglob('*') if p.is_file()}
            step(label+'_compare',[py,'-c','import sys; sys.exit(0 if sys.argv[1]=="True" else 1)',str(a==b)],needs=(label,label+'_repeat'))
    step('fixture_validate',[py,'-m','tools.asset_pipeline.validate_gltf','--root',out/'fixture','--source-root',root,'--category','object','--strict','--contract','tools/asset_pipeline/parametric/export_fixture_contract.json','--file','asset.glb','--file','asset.gltf','--output',out/'fixture-report.json'],needs=('fixture',))
    step('production_audit',[py,'-m','tools.asset_pipeline.validate_gltf','--output',out/'production-report.json'])
    project=work/'project'
    if not step('worktree',['git','worktree','add','--detach',project,rev]): return
    try:
        studio=project/'tools/asset_studio'; profile=work/'profile'; profile.mkdir()
        inventory=out/'inventory'; inventory.mkdir(); views=out/'views'; views.mkdir()
        ge=env.copy(); ge.update(APPDATA=str(profile),LOCALAPPDATA=str(profile),XDG_DATA_HOME=str(profile),FRONTLINE_INVENTORY_DIR=str(inventory),FRONTLINE_VIEWS_DIR=str(views),FRONTLINE_PILOT_DIR=str(out/'pilot'),FRONTLINE_VALIDATION_REPORT=str(out/'production-report.json'),FRONTLINE_IMPORT_REPORT=str(out/'godot-imports.json'))
        render=[godot,'--path',project,'--rendering-driver','opengl3','--audio-driver','Dummy']
        step('godot_import',render+['--editor','--import'],cwd=project,env=ge,engine=True)
        for name,script,marker,need in [('inventory','inventory_qa','ASSET_RUNTIME_INVENTORY_PASS',()),('views','capture_views','RUNTIME_VIEWS_PASS',()),('objects','world_asset_geometry_qa','WORLD_ASSET_GEOMETRY 13/13',()),('map','map_layout_qa','MAP_LAYOUT_QA 49/49',()),('pilot_godot','pilot_object_qa','PILOT_GODOT_PASS',('pilot',)),('imports','validate_imports','IMPORT_VALIDATION_COMPLETE',('production_audit',))]:
            step(name,render+['--script','res://tools/asset_pipeline/runtime/'+script+'.gd'],cwd=project,env=ge,engine=True,marker=marker,needs=('godot_import',)+need)
        suite_env=ge.copy(); suite_env['FRONTLINE_PILOT_DIR']=str(out/'suite')
        step('suite_godot',render+['--script','res://tools/asset_pipeline/runtime/pilot_suite_qa.gd'],cwd=project,env=suite_env,engine=True,marker='SUITE_GODOT_PASS 39',needs=('godot_import','suite'),timeout=1800)
        if any(r['name']=='fixture_validate' and r['status']=='passed' for r in q.rows):
            fixture=work/'fixture-import'; shutil.copytree(out/'fixture',fixture)
            (fixture/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Export QA"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n',encoding='utf-8')
            shutil.copy2(project/'tools/asset_pipeline/runtime/export_qa.gd',fixture/'export_qa.gd')
            step('fixture_godot',[godot,'--headless','--path',fixture,'--script','res://export_qa.gd'],cwd=fixture,env=ge,engine=True,marker='EXPORT_GODOT_PASS')
        step('reconcile_imports',[py,'-m','tools.asset_pipeline.reconcile_validation',out/'production-report.json',out/'godot-imports.json',out/'reconciled.json'],needs=('imports',))
        runtime=inventory/'runtime_inventory.json'
        step('reconcile_inventory',[py,'docs/qa/verify_runtime_inventory.py',runtime,inventory/'reconciliation.json'],cwd=project,needs=('inventory',))
        step('live_catalog',[py,'tools/asset_pipeline/live_catalog.py','--runtime',runtime,'--output',out/'catalog.json'],cwd=project,needs=('reconcile_inventory',))
        step('npm',[node,npm,'install','--ignore-scripts','--prefer-offline'],cwd=studio)
        step('chromium',[node,studio/'node_modules/playwright/cli.js','install','chromium'],cwd=studio,needs=('npm',),timeout=1800)
        stage=work/'studio'
        step('prepare_studio',[py,'tools/asset_studio/prepare.py',stage,'--runtime',runtime],cwd=project,needs=('npm','live_catalog'))
        step('attach_views',[py,'tools/asset_studio/attach_runtime_views.py',stage,views],cwd=project,needs=('prepare_studio','views'))
        if all(any(r['name']==n and r['status']=='passed' for r in q.rows) for n in ('attach_views','chromium')):
            handler=partial(SimpleHTTPRequestHandler,directory=str(stage))
            with ThreadingHTTPServer(('127.0.0.1',0),handler) as server:
                thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
                be=env.copy(); be.update(STUDIO_URL='http://127.0.0.1:'+str(server.server_port),REQUIRE_RUNTIME_VIEWS='1',STUDIO_EVIDENCE=str(out/'studio-evidence'),FRONTLINE_PILOT_DIR=str(out/'pilot'))
                try:
                    shutil.copy2(stage/'live_catalog.json',out/'studio-catalog.json')
                    step('browser',[node,studio/'browser_test.mjs'],cwd=studio,env=be,marker='STUDIO_RUNTIME_SCOPES_PASS',timeout=1800)
                    step('offline',[node,studio/'offline_test.mjs'],cwd=studio,env=be)
                    step('pilot_coverage',[py,'-m','tools.asset_pipeline.pilot_coverage',stage/'live_catalog.json',out/'pilot-coverage.json'],cwd=project,needs=('pilot',))
                    step('stage_pilot',[py,'-m','tools.asset_pipeline.stage_pilot',out/'pilot',stage],cwd=project,needs=('pilot_coverage',))
                    step('pilot_browser',[node,studio/'pilot_test.mjs'],cwd=studio,env=be,needs=('stage_pilot','pilot_godot'))
                    suite_be=be.copy(); suite_be['FRONTLINE_PILOT_DIR']=str(out/'suite')
                    staged=[]
                    for folder in sorted((out/'suite').glob('*/')):
                        if (folder/'pilot-report.json').is_file():
                            name='stage_suite_'+folder.name; staged.append(name)
                            step(name,[py,'-m','tools.asset_pipeline.stage_pilot',folder,stage],cwd=project,needs=('suite_godot',))
                    step('suite_browser',[node,studio/'pilot_suite_test.mjs'],cwd=studio,env=suite_be,needs=('suite_godot',*staged),timeout=1800)
                finally: server.shutdown(); thread.join()
        else:
            for name in ('browser','offline','pilot_coverage','stage_pilot','pilot_browser','suite_browser'):
                step(name,[node,'--version'],needs=('attach_views','chromium'))
    finally:
        # Preserve logs, not the isolated profile or the working tree.
        step('remove_worktree',['git','worktree','remove','--force',project])

def main():
    p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,required=True); p.add_argument('--out',type=Path,required=True); p.add_argument('--work',type=Path,required=True); p.add_argument('--godot',required=True); p.add_argument('--node',required=True); p.add_argument('--npm',required=True); p.add_argument('--previous-summary',type=Path); a=p.parse_args()
    root=a.root.resolve(); out=a.out.resolve(); work=a.work.resolve()
    if out.is_relative_to(root) or work.is_relative_to(root) or work.is_relative_to(out) or out.is_relative_to(work): raise ValueError('use separate external directories')
    rev=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    if subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).strip(): raise ValueError('checkout must be clean')
    q=QA(root,out); error=None
    try:
        work.mkdir(parents=True)
        previous=None
        if a.previous_summary:
            raw=a.previous_summary.read_bytes(); candidate=json.loads(raw)
            before=candidate['revision']
            if not re.fullmatch(r'[0-9a-f]{40}',before): raise ValueError('invalid previous revision')
            subprocess.run(['git','merge-base','--is-ancestor',before,rev],cwd=root,check=True)
            changed=subprocess.check_output(['git','diff','--name-only','-z',before,rev],cwd=root).decode('utf-8').split('\0')
            # Only changes outside the actual game and LOD runner permit deferring
            # the three expensive LOD captures. Never label prior evidence passed.
            permitted={'.gitattributes','tests/test_qa_windows_contract.py','tools/asset_pipeline/runtime/world_asset_geometry_qa.gd','tools/asset_pipeline/parametric/export_fixture.py','tools/asset_pipeline/parametric/pilot_object.py','tools/asset_pipeline/parametric/pilot_suite.py'}
            if all(not p or p in permitted or p.startswith(('docs/','tools/qa_all_in_one/')) for p in changed):
                previous={**candidate,'summary_sha256':hashlib.sha256(raw).hexdigest()}
            else:
                print('Game or other pipeline sources changed; rerunning all LOD modes.',flush=True)
        run(q,rev,a.godot,a.node,a.npm,work,previous)
    except Exception as exc:
        error=repr(exc); print(error,flush=True)
    return q.finish(rev,error)

if __name__=='__main__': raise SystemExit(main())
