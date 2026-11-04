"""Motores de cuenta y de campana (frente 5F, 2026-11-04).
- PropCycle: el motor de reglas de cuenta en C# (NQMaster.cs, via mono), su port en Python y el motor de investigacion dan lo mismo
  en 780 casos al azar (tools/propcycle_test/run_test.py; lento, ~35 s).
- objective.py: el flujo de caja por asiento reproduce exactamente prop_wf.seat (2.400 asientos, ~10 s).
- tools/verify_patch_chain.py: la cadena archivada v4.3 -> v4.4 reproduce el sha256 de la consolidacion."""
import sys, unittest
from tests._util import MINE, HAS_MONO, lento, run


class Engines(unittest.TestCase):
    @lento
    @unittest.skipUnless(HAS_MONO, "sin mono / mcs")
    def test_propcycle_three_way(self):
        r = run([sys.executable, "tools/propcycle_test/run_test.py"], timeout=900)
        self.assertEqual(r.returncode, 0, r.stdout[-800:] + r.stderr[-800:])
        self.assertIn("mismatches C# vs research 0 | python port vs research 0", r.stdout)

    def test_objective_selftest(self):
        r = run([sys.executable, "objective.py", "selftest"], cwd=MINE, timeout=900)
        self.assertEqual(r.returncode, 0, r.stdout[-800:] + r.stderr[-800:])
        self.assertIn(" 0 diferencias contra prop_wf.seat", r.stdout)

    def test_patch_chain_history(self):
        r = run([sys.executable, "tools/verify_patch_chain.py"], timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
