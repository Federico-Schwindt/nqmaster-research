"""verify_patch_chain.py (2026-11-04, frente 5F): reproduce la ultima cadena de parches (v4.3 -> v4.4) en una carpeta temporal.

NQMaster.cs es la fuente unica desde el 2026-11-04 y los parches estan archivados en archive/patches/ (README alli). Este script copia el
backup y los 7 parches a una carpeta temporal con la estructura original (research/mine/), los aplica en orden y compara el resultado con
el sha256 de la consolidacion. Sirve para auditar la historia; no toca el repo.
Run: python3 tools/verify_patch_chain.py   (sale 0 si la cadena reproduce el sha registrado)"""
import hashlib, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAIN = ["patch_fillseries", "patch_parity_s2", "patch_clock_check", "patch_open_risk", "patch_live_safety", "patch_edge_restore", "patch_panel_risk"]
SHA = "85c0a3ef5e6f556dc5870d5ea1aea90b569f5ae17fdd4cfabfc42f97fe84f687"


def main():
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "research", "mine")); os.makedirs(os.path.join(td, "archive", "backups"))
        bk = os.path.join(ROOT, "archive", "backups", "NQMaster_backup_pre_fillseries.cs")
        shutil.copy(bk, os.path.join(td, "archive", "backups")); shutil.copy(bk, os.path.join(td, "NQMaster.cs"))
        for p in CHAIN:
            shutil.copy(os.path.join(ROOT, "archive", "patches", p + ".py"), os.path.join(td, "research", "mine"))
        for p in CHAIN:
            r = subprocess.run([sys.executable, os.path.join(td, "research", "mine", p + ".py")], capture_output=True, text=True)
            if r.returncode != 0: print("FALLA", p, r.stdout[-300:], r.stderr[-300:]); return 1
        h = hashlib.sha256(open(os.path.join(td, "NQMaster.cs"), "rb").read()).hexdigest()
    ok = h == SHA
    print("cadena v4.3 -> v4.4:", h, "OK (igual a la consolidacion)" if ok else "DISTINTA de la consolidacion " + SHA)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
