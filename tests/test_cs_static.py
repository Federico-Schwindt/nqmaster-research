"""NinjaScript sin NinjaTrader: lo que se puede verificar en la nube antes de pedir F5 (frente 5F, 2026-11-04).
- cada .cs type-checkea contra el stub (C# 5, mcs);
- cada string.Format tiene los argumentos que piden sus placeholders (una FormatException en vivo frena el panel o un aviso);
- ningun parametro se llama como una palabra contextual (NinjaTrader las rechaza aunque mcs las acepte: error de F5 del 17-oct);
- cada estado que frena la operacion tiene su texto en castellano en el panel."""
import os, re, sys, unittest
from tests._util import ROOT, CS_FILES, HAS_MONO, read, run
sys.path.insert(0, os.path.join(ROOT, "tools"))
import fmtcheck

CONTEXTUAL = {"when", "value", "var", "from", "with", "and", "or", "not", "on", "select", "where", "group", "into", "orderby", "join",
              "let", "by", "ascending", "descending", "equals", "yield", "async", "await", "dynamic", "nameof", "global", "partial",
              "record", "init", "managed", "unmanaged", "nint", "nuint", "notnull"}
DECL = re.compile(r"^[ \t]*(?:\[[^\]]*\][ \t]*)*(?:(?:public|private|protected|internal|static|override|virtual|abstract|sealed|new|extern|unsafe)[ \t]+)+"
                  r"[\w<>\[\],. ?]+?[ \t]+(\w+)[ \t]*\(([^()]*(?:\([^()]*\)[^()]*)*)\)", re.M)


def param_names(plist):
    out, depth, cur = [], 0, ""
    for c in plist + ",":
        if c in "<([": depth += 1
        elif c in ">)]": depth -= 1
        if c == "," and depth == 0:
            p = cur.split("=")[0].strip()
            if p: out.append(re.findall(r"\w+", p)[-1])
            cur = ""
        else: cur += c
    return out


class CsStatic(unittest.TestCase):
    @unittest.skipUnless(HAS_MONO, "sin mono / mcs")
    def test_stub_typecheck(self):
        for f in CS_FILES:
            r = run(["bash", "tools/nt8_stub/check.sh", f])
            self.assertEqual(r.returncode, 0, "%s no type-checkea contra el stub:\n%s" % (f, r.stdout + r.stderr))

    def test_string_format(self):
        for f in CS_FILES:
            n, bad = fmtcheck.check(os.path.join(ROOT, f))
            self.assertEqual(bad, [], "%s: string.Format sospechosos" % f)
        self.assertGreater(fmtcheck.check(os.path.join(ROOT, "NQMaster.cs"))[0], 100)

    def test_contextual_keyword_parameters(self):
        found = []
        for f in CS_FILES:
            src = read(f)
            for m in DECL.finditer(src):
                for p in param_names(m.group(2)):
                    if p in CONTEXTUAL: found.append("%s:%d %s(... %s ...)" % (f, src.count("\n", 0, m.start()) + 1, m.group(1), p))
        self.assertEqual(found, [], "parametros con nombre de palabra contextual (NinjaTrader no compila)")

    def test_declaration_scan_sees_methods(self):              # the scan above must actually see the methods (guards the regex)
        names = {m.group(1) for m in DECL.finditer(read("NQMaster.cs"))}
        for nm in ("OnBarUpdate", "OnExecutionUpdate", "ExitModule", "PropGoLive", "EdgeRestore", "UsEtFromUtc", "PrintModuleReport"):
            self.assertIn(nm, names)

    def test_status_translations(self):
        src = read("NQMaster.cs")
        body = src[src.index("private string StatusEs()"):]; body = body[:body.index("\n\t\t}\n")]
        missing = []
        for lit in sorted(set(re.findall(r'status = "([^"]*)"', src))):
            if lit in ("trading", "waiting"): continue
            if ('case "%s":' % lit) not in body and ('StartsWith("%s"' % lit) not in body: missing.append(lit)
        self.assertEqual(missing, [], "estados sin texto en castellano en StatusEs")

    def test_source_of_truth_header(self):
        self.assertIn("SOURCE OF TRUTH since 2026-11-04", read("NQMaster.cs"))


if __name__ == "__main__":
    unittest.main()
