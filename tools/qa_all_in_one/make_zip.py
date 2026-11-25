"""Package the committed Windows bootstrap, pinned to the clean integrated HEAD."""
from pathlib import Path
import argparse
import subprocess
import zipfile

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('output', type=Path)
a = p.parse_args()
root = Path(__file__).resolve().parents[2]
output = a.output.resolve()
if output.is_relative_to(root): raise ValueError('output must be outside repo')
def git(*args): return subprocess.check_output(['git', '-C', str(root), *args])
if git('status','--porcelain').strip(): raise ValueError('checkout must be clean')
rev = git('rev-parse','HEAD').decode().strip()
with zipfile.ZipFile(output,'x',zipfile.ZIP_DEFLATED) as z:
    for name in ('TESTAR_TUDO.bat','bootstrap.ps1','LEIA-ME.txt'):
        z.writestr(name,git('show',rev+':tools/qa_all_in_one/'+name))
    z.writestr('REVISION.txt',rev+'\n')
with zipfile.ZipFile(output) as z:
    if z.testzip() is not None: raise RuntimeError('ZIP integrity check failed')
print(output, rev)
