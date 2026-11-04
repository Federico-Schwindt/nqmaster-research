"""fmtcheck.py (2026-11-04, frente 5F; antes docs/experimentos/revisiones/codigo_2026-10-29/cr_fmtcheck.py): cada string.Format / String.Format /
.AppendFormat( ... ) de un archivo C# tiene un formato literal bien formado (llaves balanceadas, items {n[,ancho][:formato]}) y al menos tantos
argumentos como pide su placeholder mas alto. Un {3} con 3 argumentos o una llave suelta tira FormatException en vivo (NinjaTrader la ve recien
cuando se ejecuta esa linea, y en OnBarUpdate deshabilita la estrategia).
Run: python3 tools/fmtcheck.py NQMaster.cs   (sale 1 si hay alguna sospechosa)"""
import re, sys

CALL = re.compile(r"(?:\b[sS]tring\.Format|\.AppendFormat)\(")


def well_formed(fmt):
    """.NET composite format grammar on the raw literal text: {{ and }} escapes, items {index[,alignment][:format]}, no stray braces."""
    i = 0
    while i < len(fmt):
        c = fmt[i]
        if c == "{":
            if fmt[i + 1:i + 2] == "{": i += 2; continue
            j = fmt.find("}", i)
            if j < 0 or not re.fullmatch(r"\s*\d+\s*(,\s*-?\d+\s*)?(:[^{}]*)?", fmt[i + 1:j]): return False
            i = j + 1
        elif c == "}":
            if fmt[i + 1:i + 2] == "}": i += 2; continue
            return False
        else: i += 1
    return True


def check(path):
    src = open(path, encoding="utf-8-sig").read()
    i = 0; n = 0; bad = []
    while True:
        mm = CALL.search(src, i)
        if not mm: break
        k = mm.start(); j = mm.end()
        depth = 1; args = []; cur = ""; instr = False; esc = False; inchar = False
        while depth > 0 and j < len(src):
            c = src[j]
            if instr:
                cur += c
                if esc: esc = False
                elif c == "\\": esc = True
                elif c == '"': instr = False
            elif inchar:
                cur += c
                if esc: esc = False
                elif c == "\\": esc = True
                elif c == "'": inchar = False
            else:
                if c == '"': instr = True; cur += c
                elif c == "'": inchar = True; cur += c
                elif c in "([{": depth += 1; cur += c
                elif c in ")]}":
                    depth -= 1
                    if depth == 0: args.append(cur); break
                    cur += c
                elif c == "," and depth == 1: args.append(cur); cur = ""
                else: cur += c
            j += 1
        line = src.count("\n", 0, k) + 1
        a0 = args[0].strip(); off = 0
        if a0.startswith("CultureInfo"): a0 = args[1].strip(); off = 1
        lits = re.findall(r'"((?:[^"\\]|\\.)*)"', a0); fmt = "".join(lits)
        idx = [int(m) for m in re.findall(r"(?<!\{)\{(\d+)", fmt.replace("{{", "").replace("}}", ""))]
        nargs = len(args) - 1 - off; mx = max(idx) + 1 if idx else 0
        n += 1
        if mx > nargs or not lits: bad.append("line %d: placeholders need %d, args %d: %r" % (line, mx, nargs, fmt[:90]))
        elif not well_formed(fmt): bad.append("line %d: malformed format string: %r" % (line, fmt[:90]))
        i = j
    return n, bad


if __name__ == "__main__":
    n, bad = check(sys.argv[1])
    for b in bad: print(b)
    print("calls", n, "suspicious", len(bad))
    sys.exit(1 if bad else 0)
