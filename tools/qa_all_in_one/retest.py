"""Reuse a completed Windows QA installation; preserve prior evidence."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from datetime import datetime
import uuid

PRIOR_REVISION = '95c7ac8c0b32c7c5723ab33cb7a2d4dd29d52968'
PRIOR_SUMMARY_SHA = '3b574ae73109cea34ac16fb48a389a5880d85143f7123c892fa469d7a64a4ffc'
REPO_URL = 'https://github.com/TPollTech/Frontline-Survival.git'


def prior_summary(base):
    path = base / 'evidence' / 'summary.json'
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PRIOR_SUMMARY_SHA:
        raise ValueError('Previous summary differs from the reviewed evidence; do not overwrite it.')
    data = json.loads(raw)
    if data.get('revision') != PRIOR_REVISION:
        raise ValueError('Unexpected previous revision')
    if not all(any(s['name'] == mode and s['status'] == 'passed' for s in data['steps']) for mode in ('lod', 'benchmark', 'motion')):
        raise ValueError('Prior LOD evidence is incomplete')
    return path


def executable(folder, name):
    found = sorted(folder.rglob(name))
    if len(found) != 1 or not found[0].is_file():
        raise FileNotFoundError(f'Expected exactly one {name} in {folder}')
    return found[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous', type=Path, required=True)
    parser.add_argument('--revision-file', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    base = args.previous.resolve()
    dest = args.destination.resolve()
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6]
    run = base.parent / ('retest-' + stamp)
    run.mkdir(parents=True)
    log = run / 'setup-retest.log'
    out = run / 'evidence'
    rc = 1
    source = base / 'source'
    checkout = run / 'source'
    try:
        revision = args.revision_file.read_text(encoding='ascii').strip()
        if not re.fullmatch(r'[0-9a-f]{40}', revision):
            raise ValueError('Invalid pinned revision')
        prior = prior_summary(base)
        godot = executable(base / 'godot', 'Godot_v4.4.1-stable_win64_console.exe')
        node = executable(base / 'node', 'node.exe')
        blender = executable(base / 'blender', 'blender.exe')
        npm = node.parent / 'node_modules/npm/bin/npm-cli.js'
        if not npm.is_file():
            raise FileNotFoundError(npm)
        git = shutil.which('git')
        if not git:
            raise FileNotFoundError('Git not available in PATH')
        def git_output(*cmd):
            return subprocess.check_output([git, '-C', str(source), *cmd], text=True).strip()
        if git_output('remote', 'get-url', 'origin').rstrip('/') != REPO_URL:
            raise ValueError('Unexpected origin remote')
        env = os.environ.copy()
        env.update(FRONTLINE_BLENDER=str(blender), PLAYWRIGHT_BROWSERS_PATH=str(base / 'work' / 'browsers'), PYTHONDONTWRITEBYTECODE='1')
        env['PATH'] = os.pathsep.join((str(node.parent), str(godot.parent), str(Path(git).parent), env['PATH']))
        with log.open('w', encoding='utf-8') as stream:
            stream.write(f'Prior revision {PRIOR_REVISION}\nRequested revision {revision}\n')
            stream.flush()
            def checked(*cmd):
                print('Setup:', cmd[0], ' '.join(map(str, cmd[1:4])), flush=True)
                subprocess.run([str(x) for x in cmd], check=True, env=env, stdout=stream, stderr=subprocess.STDOUT)
            checked(git, '-C', source, 'fetch', '--no-tags', 'origin', 'main')
            checked(git, '-C', source, 'merge-base', '--is-ancestor', PRIOR_REVISION, revision)
            checked(git, '-C', source, 'merge-base', '--is-ancestor', revision, 'FETCH_HEAD')
            checked(git, '-C', source, '-c', 'core.autocrlf=false', 'worktree', 'add', '--detach', checkout, revision)
            checked(sys.executable, '-c', 'import numpy, trimesh, scipy; print(numpy.__version__,trimesh.__version__,scipy.__version__)')
        print('Starting incremental QA. Prior LOD captures remain in the original evidence folder.', flush=True)
        result = subprocess.run([sys.executable, str(checkout / 'tools/qa_all_in_one/run.py'), '--root', str(checkout), '--out', str(out), '--work', str(run / 'work'), '--godot', str(godot), '--node', str(node), '--npm', str(npm), '--previous-summary', str(prior)], env=env)
        rc = result.returncode
        with log.open('a', encoding='utf-8') as stream:
            stream.write(f'Runner exit code: {rc}\n')
    except Exception as exc:
        with log.open('a', encoding='utf-8') as stream:
            stream.write(repr(exc) + '\n')
        print('Setup failed:', exc, flush=True)
    finally:
        # Keep the previous evidence and checkout. Only export the new report.
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(log, dest / ('SETUP-RETESTE-' + stamp + '.log'))
        if out.with_suffix('.zip').is_file():
            target = dest / ('RESULTADOS-RETESTE-' + stamp + '.zip')
            shutil.copy2(out.with_suffix('.zip'), target)
            print('Send:', target, flush=True)
        else:
            print('Send the SETUP-RETESTE log; no evidence ZIP was created.', flush=True)
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
