"""Funciones puras de NQMaster.cs compiladas con mcs y corridas con mono, contra una referencia independiente (frente 5F, 2026-11-04).
- UsEtFromUtc (control de reloj): la regla fija de horario de verano de EE.UU. contra la base de zonas horarias (America/New_York),
  cada 15 minutos 2010-2035: mismos cambios de offset.
- EdgeParse / KeyDate (monitor de borde): archivos validos, fecha 0, campos ilegibles, fechas imposibles, NaN y negativos."""
import datetime as dt, unittest
from zoneinfo import ZoneInfo
from tests._util import HAS_MONO, read, cs_method, mono_run


@unittest.skipUnless(HAS_MONO, "sin mono / mcs")
class CsMono(unittest.TestCase):
    def test_us_dst_rule(self):
        fn = cs_method(read("NQMaster.cs"), "private static DateTime UsEtFromUtc(").replace("private static", "static")
        code = """using System; class T { %s
  static void Main() { DateTime t = new DateTime(2010, 1, 1, 0, 0, 0, DateTimeKind.Utc), end = new DateTime(2036, 1, 1, 0, 0, 0, DateTimeKind.Utc); double prev = 99;
    for (; t < end; t = t.AddMinutes(15)) { double off = (UsEtFromUtc(t) - t).TotalHours; if (off != prev) { Console.WriteLine(t.ToString("yyyy-MM-dd HH:mm") + " " + off); prev = off; } } } }""" % fn
        got = mono_run(code).split("\n")
        ny, t, prev, ref = ZoneInfo("America/New_York"), dt.datetime(2010, 1, 1, tzinfo=dt.timezone.utc), None, []
        while t < dt.datetime(2036, 1, 1, tzinfo=dt.timezone.utc):
            off = t.astimezone(ny).utcoffset().total_seconds() / 3600
            if off != prev: ref.append("%s %s" % (t.strftime("%Y-%m-%d %H:%M"), int(off))); prev = off
            t += dt.timedelta(minutes=15)
        got = [g.strip() for g in got if g.strip()]
        self.assertEqual(len(ref), 1 + 2 * 26)          # the initial offset + 52 changes
        self.assertEqual(got, ref)

    def test_edge_parse(self):
        src = read("NQMaster.cs")
        fn = cs_method(src, "private static bool EdgeParse(").replace("private static", "static")
        kd = cs_method(src, "private static DateTime KeyDate(").replace("private static", "static")
        cases = [("Ultra;20261028;3.5;20;0;0;;0;2026-10-05;0.0899;26.93", True), ("Ultra;0;0;0;0;0;;0;2026-10-05", True),
                 ("Ultra;20261028;x;20;0;0;;0;2026-10-05", False), ("Ultra;20261328;3.5;20;0;0;;0;2026-10-05", False),
                 ("Ultra;20260231;3.5;20;0;0;;0;2026-10-05", False), ("Ultra;19991231;3.5;20;0;0;;0;2026-10-05", False),
                 ("Ultra;20261028;NaN;20;0;0;;0;2026-10-05", False), ("Ultra;20261028;-1;20;0;0;;0;2026-10-05", False),
                 ("Ultra;20261028;3.5;-2;0;0;;0;2026-10-05", False), ("Ultra;20261028;3.5;20;0;-1;;0;2026-10-05", False), ("Ultra;20261028;3.5", False),
                 ("Ultra;20261028;3.5;20;1;250;REV06 MOM13;1;2026-10-05;0.0899;26.93", True)]
        code = """using System; using System.Collections.Generic; using System.Globalization; class T { %s %s
  static void Main() { string[] c = { %s };
    foreach (string x in c) { int d, days, fb; double sv; bool al, wn; List<string> off;
      bool ok = EdgeParse(x.Split(';'), out d, out sv, out days, out al, out fb, out wn, out off);
      Console.WriteLine(ok + "|" + (ok ? d + "|" + days + "|" + al + "|" + fb + "|" + string.Join(",", off.ToArray()) : "")); }
    Console.WriteLine(KeyDate(20261028).ToString("yyyy-MM-dd")); } }""" % (fn, kd, ", ".join('"%s"' % c for c, _ in cases))
        out = [l.strip() for l in mono_run(code).split("\n") if l.strip()]
        self.assertEqual([o.split("|")[0] == "True" for o in out[:-1]], [e for _, e in cases])
        self.assertEqual(out[-2], "True|20261028|20|True|250|REV06,MOM13")
        self.assertEqual(out[-1], "2026-10-28")


if __name__ == "__main__":
    unittest.main()
