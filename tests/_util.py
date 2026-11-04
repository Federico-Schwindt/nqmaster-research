"""Ayudas comunes de los tests (frente 5F, 2026-11-04)."""
import os, re, shutil, subprocess, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MINE = os.path.join(ROOT, "research", "mine")
RAPIDO = os.environ.get("NQ_TESTS_RAPIDO") == "1"          # tools/run_tests.sh --rapido: saltea los tests de mas de ~30 s
HAS_MONO = shutil.which("mcs") is not None and shutil.which("mono") is not None
CS_FILES = ["NQMaster.cs", "NQAccountGuard.cs", "OrderFlowRecorder.cs", "BarExporterUTC.cs"]


def lento(test):
    return unittest.skipIf(RAPIDO, "test lento (tools/run_tests.sh sin --rapido)")(test)


def read(rel):
    return open(os.path.join(ROOT, rel), encoding="utf-8-sig").read()


def run(cmd, cwd=ROOT, timeout=900):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)


def cs_method(src, head):
    """The text of a C# member that starts with `head` (e.g. 'private static DateTime UsEtFromUtc('), braces matched."""
    i = src.index(head); j = src.index("{", i); depth = 0
    for k in range(j, len(src)):
        if src[k] == "{": depth += 1
        elif src[k] == "}":
            depth -= 1
            if depth == 0: return src[i:k + 1]
    raise ValueError("unbalanced braces after " + head)


def mono_run(code):
    """Compile `code` (a complete C# 5 program with Main) with mcs and run it with mono; returns stdout."""
    with tempfile.TemporaryDirectory() as td:
        cs, exe = os.path.join(td, "t.cs"), os.path.join(td, "t.exe")
        open(cs, "w", encoding="utf-8").write(code)
        r = subprocess.run(["mcs", "-langversion:5", "-out:" + exe, cs], capture_output=True, text=True)
        if r.returncode != 0: raise AssertionError("mcs:\n" + r.stdout + r.stderr)
        r = subprocess.run(["mono", exe], capture_output=True, text=True, timeout=300)
        if r.returncode != 0: raise AssertionError("mono:\n" + r.stdout + r.stderr)
        return r.stdout
