"""Regression for raw Git bytes under Windows autocrlf and canonical paths."""
from pathlib import Path, PureWindowsPath, PurePosixPath
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class WindowsQAContract(unittest.TestCase):
    def test_raw_bytes_in_new_worktree(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / 'source'
            repo.mkdir()
            def git(cwd, *args):
                return subprocess.check_output(['git', '-C', str(cwd), *args], stderr=subprocess.STDOUT).strip()
            git(repo, 'init', '-q')
            git(repo, 'config', 'user.email', 'qa@example.invalid')
            git(repo, 'config', 'user.name', 'QA')
            git(repo, 'config', 'core.autocrlf', 'false')
            files = {'manifest.json': b'{"asset":1}\n', 'source.py': b'print(1)\n', 'workflow.yml': b'name: qa\n', 'asset.glb': b'\x00\r\n\xff'}
            for path, data in files.items():
                (repo / path).write_bytes(data)
            git(repo, 'add', '.')
            git(repo, 'commit', '-qm', 'base')
            old = root / 'old'
            git(root, '-c', 'core.autocrlf=true', 'clone', '-q', str(repo), str(old))
            self.assertNotEqual((old / 'manifest.json').read_bytes(), files['manifest.json'])
            attrs = (ROOT / '.gitattributes').read_bytes()
            (repo / '.gitattributes').write_bytes(attrs)
            git(repo, 'add', '.gitattributes')
            git(repo, 'commit', '-qm', 'preserve bytes')
            git(old, 'fetch', '-q', 'origin')
            target = root / 'retest'
            git(old, '-c', 'core.autocrlf=true', 'worktree', 'add', '-q', '--detach', str(target), 'FETCH_HEAD')
            for path, data in {**files, '.gitattributes': attrs}.items():
                self.assertEqual((target / path).read_bytes(), data, path)
                self.assertEqual(git(target, 'hash-object', '--no-filters', path), git(target, 'rev-parse', 'HEAD:' + path), path)
            (target / 'source.py').write_bytes(b'print(2)\n')
            self.assertNotEqual(git(target, 'hash-object', '--no-filters', 'source.py'), git(target, 'rev-parse', 'HEAD:source.py'))

    def test_windows_source_paths(self):
        root = PureWindowsPath('C:/qa/source')
        path = root / 'tools/asset_pipeline/parametric/export_fixture.py'
        relative = path.relative_to(root)
        self.assertIn('\\', str(relative))
        canonical = relative.as_posix()
        self.assertEqual(canonical, 'tools/asset_pipeline/parametric/export_fixture.py')
        p = PurePosixPath(canonical)
        self.assertFalse(p.is_absolute())
        self.assertNotIn('..', p.parts)
        self.assertNotIn('\\', canonical)
        self.assertNotIn(':', canonical)
        self.assertEqual(str(p), canonical)

if __name__ == '__main__':
    unittest.main()
