"""NinjaScript sin NinjaTrader: lo que se puede verificar en la nube antes de pedir F5 (frente 5F, 2026-11-04).
- cada .cs type-checkea contra el stub (C# 5, mcs);
- cada string.Format tiene los argumentos que piden sus placeholders (una FormatException en vivo frena el panel o un aviso);
- ningun parametro se llama como una palabra contextual (NinjaTrader rechazo 'when' en el F5 del 17-oct aunque mcs lo aceptaba; la lista de
  CLAUDE.md y las palabras de LINQ, por las dudas): con mono, por reflexion sobre el ensamblado compilado contra el stub (ve metodos, constructores,
  lambdas y delegados); sin mono, con un regex de declaraciones (ve el caso normal);
- cada estado que frena la operacion tiene su texto en castellano en el panel."""
import os, re, subprocess, sys, tempfile, unittest
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

    @unittest.skipUnless(HAS_MONO, "sin mono / mcs")
    def test_contextual_keyword_parameters_reflection(self):
        stub = os.path.join(ROOT, "tools", "nt8_stub", "NT8ApiStub.cs")
        # property / event accessors (IsSpecialName, e.g. set_X(value)) are not declared parameters: skipped
        refl = """using System; using System.Reflection; class R { static void Main(string[] a) {
  BindingFlags f = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly;
  foreach (Type t in Assembly.LoadFrom(a[0]).GetTypes()) { foreach (MethodBase m in t.GetMethods(f)) { if (m.IsSpecialName) continue; foreach (ParameterInfo p in m.GetParameters()) Console.WriteLine(t.FullName + "." + m.Name + " " + p.Name); }
    foreach (MethodBase m in t.GetConstructors(f)) foreach (ParameterInfo p in m.GetParameters()) Console.WriteLine(t.FullName + "..ctor " + p.Name); } } }"""
        found, seen = [], 0
        with tempfile.TemporaryDirectory() as td:
            sd = os.path.join(td, "NT8ApiStub.dll"); open(os.path.join(td, "r.cs"), "w").write(refl)
            for cmd in (["mcs", "-langversion:5", "-target:library", "-out:" + sd, stub], ["mcs", "-out:" + os.path.join(td, "r.exe"), os.path.join(td, "r.cs")]):
                rr = subprocess.run(cmd, capture_output=True, text=True); self.assertEqual(rr.returncode, 0, rr.stdout + rr.stderr)
            for f in CS_FILES:
                ud = os.path.join(td, f[:-3] + ".dll")
                rr = subprocess.run(["mcs", "-langversion:5", "-target:library", "-r:" + sd, "-out:" + ud, os.path.join(ROOT, f)], capture_output=True, text=True)
                self.assertEqual(rr.returncode, 0, f + ": " + rr.stdout[-600:])
                rr = subprocess.run(["mono", os.path.join(td, "r.exe"), ud], capture_output=True, text=True, cwd=td)
                self.assertEqual(rr.returncode, 0, rr.stdout[-600:] + rr.stderr[-600:])
                for line in rr.stdout.splitlines():
                    seen += 1; who, p = line.rsplit(" ", 1)
                    if p in CONTEXTUAL: found.append("%s: %s(%s)" % (f, who, p))
        self.assertGreater(seen, 100)
        self.assertEqual(found, [], "parametros con nombre de palabra contextual (NinjaTrader no compila)")

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
        lits = set()
        for rhs in re.findall(r'\bstatus\s*=(?!=)([^;]*);', src):
            ls = re.findall(r'"((?:[^"\\]|\\.)*)"', rhs)
            if ls and ('StartsWith("%s"' % ls[0]) in body: continue              # a concatenation translated by its prefix (low volatility)
            lits.update(ls)
        self.assertGreater(len(lits), 10)
        for lit in sorted(lits):
            if lit in ("trading", "waiting") or "\\u00" in lit or any(ord(ch) > 127 for ch in lit): continue      # already Spanish
            if ('case "%s":' % lit) not in body and ('StartsWith("%s"' % lit) not in body: missing.append(lit)
        self.assertEqual(missing, [], "estados sin texto en castellano en StatusEs")

    def test_source_of_truth_header(self):
        self.assertIn("SOURCE OF TRUTH since 2026-11-04", read("NQMaster.cs"))


if __name__ == "__main__":
    unittest.main()
