"""La cadena de datos de la investigacion (frente 5F, 2026-11-04): de los .npz restaurados a las listas de trades y los caminos de campana.
- los archivos grandes coinciden con el SHA-256 del manifiesto (lento: ~4 min de disco);
- los precios de 1 minuto que usan IS / C24 / REAL / regimen tienen la forma esperada (OHLC coherente, fechas y sesiones en orden);
- las listas de trades de referencia (research_set 'ultra_d4' de campana y 'ultra_d4_mnq' de paridad) no cambiaron en silencio;
- si existe la cache de caminos de campana (acct2027_paths.pkl), sigue siendo la construida sobre la lista corregida del 27-oct.
Las huellas se regeneran SOLO a proposito: python3 -m tests.test_data_chain --record (y se commitea el cambio con el motivo)."""
import hashlib, json, os, pickle, sys, unittest
import numpy as np
from tests._util import ROOT, MINE, lento, run

FIX = os.path.join(ROOT, "tests", "fixtures", "data_chain.json")
# file: (first date at most, last date at least): IS / C24 CFD 2020-26, REAL MNQ 2024-26, NQ real 2010-26, regime CFD 2015-26
PRICES = {"nq_1m.npz": (20200110, 20260901), "mnq_fut.npz": (20240110, 20260901), "nqdb.npz": (20100701, 20261001), "nqhd_long.npz": (20150110, 20260901)}
CACHE = os.path.join(ROOT, "research", "tmp", "scratch", "acct2027_paths.pkl")


def set_hash(name):
    sys.path.insert(0, MINE); cwd = os.getcwd(); os.chdir(MINE)
    try:
        from nt_compare import research_set
        X = research_set(name)[0][["date", "mod", "tin", "tout", "d", "u", "w"]].sort_values(["date", "tin", "mod"]).reset_index(drop=True)
    finally: os.chdir(cwd)
    txt = X.to_csv(index=False, float_format="%.6f")
    return hashlib.sha256(txt.encode()).hexdigest(), len(X)


def cache_hash():
    days, P = pickle.load(open(CACHE, "rb")); h = hashlib.sha256(np.ascontiguousarray(np.asarray(days)).tobytes())
    for cap in sorted(P):
        a, b, ca, cb = P[cap]
        for arr in list(a) + list(b) + [ca, cb]: h.update(np.round(np.ascontiguousarray(arr, dtype=np.float64), 6).tobytes())
    return h.hexdigest()


def fixtures():
    return json.load(open(FIX)) if os.path.exists(FIX) else {}


class DataChain(unittest.TestCase):
    @lento
    def test_manifest_sha256(self):
        r = run([sys.executable, "tools/restore_data.py", "--check"], timeout=1800)
        self.assertEqual(r.returncode, 0, "datos distintos del manifiesto:\n" + "\n".join(l for l in r.stdout.splitlines() if not l.startswith("ok")))

    def test_price_files(self):
        for f, (first, last) in PRICES.items():
            p = os.path.join(ROOT, "research", "data", f)
            if not os.path.exists(p): self.fail("%s no existe: bash tools/cloud_setup.sh" % f)
            z = np.load(p); o, h, l, c = (z[k] for k in "ohlc"); om, day, date = z["om"], z["dayid"], z["date"]
            n = len(c)
            with self.subTest(archivo=f):
                self.assertTrue(all(len(z[k]) == n for k in ("o", "h", "l", "c", "v", "om", "dayid", "date")))
                self.assertFalse(np.isnan(np.concatenate([o, h, l, c])).any())
                self.assertTrue((h >= np.maximum(o, c) - 1e-9).all() and (l <= np.minimum(o, c) + 1e-9).all())
                self.assertTrue((np.diff(date) >= 0).all() and (np.diff(day) >= 0).all())
                self.assertTrue(((om >= 0) & (om < 1440)).all())
                self.assertLessEqual(int(date[0]), first); self.assertGreaterEqual(int(date[-1]), last)

    def test_research_sets(self):
        fx = fixtures().get("research_sets", {})
        for name in ("ultra_d4", "ultra_d4_mnq"):
            with self.subTest(set=name):
                self.assertIn(name, fx, "sin huella: python3 -m tests.test_data_chain --record")
                h, n = set_hash(name)
                self.assertEqual((h, n), (fx[name]["sha256"], fx[name]["trades"]), "%s cambio: si fue a proposito, regrabar la huella y anotar por que" % name)

    def test_campaign_paths_cache(self):
        if not os.path.exists(CACHE): self.skipTest("sin cache de caminos (research/tmp/scratch/acct2027_paths.pkl): se construye con acct_2027.build()")
        fx = fixtures().get("acct2027_paths")
        self.assertIsNotNone(fx, "sin huella: python3 -m tests.test_data_chain --record")
        self.assertEqual(cache_hash(), fx, "la cache de caminos de campana no es la registrada: reconstruirla desde la lista corregida")


if __name__ == "__main__":
    if "--record" in sys.argv:
        fx = fixtures(); fx["research_sets"] = {}
        for name in ("ultra_d4", "ultra_d4_mnq"):
            h, n = set_hash(name); fx["research_sets"][name] = dict(sha256=h, trades=n)
        if os.path.exists(CACHE): fx["acct2027_paths"] = cache_hash()
        os.makedirs(os.path.dirname(FIX), exist_ok=True); json.dump(fx, open(FIX, "w"), indent=1); print(json.dumps(fx, indent=1))
    else:
        unittest.main()
