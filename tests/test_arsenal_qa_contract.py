"""Checks complete registry coverage and report/CI wiring."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ArsenalQAContracts(unittest.TestCase):
    def test_all_registered_weapons_covered(self):
        player = (ROOT / 'scripts/player.gd').read_text()
        qa = (ROOT / 'tests/arsenal_qa.gd').read_text()
        registry = player.split('const WEAPONS = {', 1)[1].split('\n}', 1)[0]
        ids = set(re.findall(r'"(\w+)":\s*\{"name"', registry))
        cases = set(re.findall(r'"(\w+)"', qa.split('const IDS: Array[String] = ', 1)[1].split('\n', 1)[0]))
        self.assertEqual(ids, cases)
        self.assertEqual(len(ids), 8)
        for marker in ('real collision target receives expected game damage', 'full reload conserves ammunition',
                       'mechanical cycle blocks shot', 'attachments survive switch', 'ammunition survives switch'):
            self.assertIn(marker, qa)

    def test_report_and_visual_gate(self):
        workflow = (ROOT / '.github/workflows/windows-build.yml').read_text()
        visual = (ROOT / 'tests/viewmodel_framing_qa.gd').read_text()
        self.assertIn('QA_ARSENAL_PASS', workflow)
        self.assertIn('docs/qa/arsenal_report.json', workflow)
        self.assertIn('CELL.x * 3', visual)
        self.assertIn('reload animation did not lower visual rig', visual)
