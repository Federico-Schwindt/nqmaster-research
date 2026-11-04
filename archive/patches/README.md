# Parches históricos de `NQMaster.cs` (no se corren)

Desde el 2026-11-04 (frente 5F), **`NQMaster.cs` es la fuente única**: se edita directamente. Antes de cada F5 hay que correr `bash tools/nt8_stub/check.sh NQMaster.cs` y `bash tools/run_tests.sh`.

Los `patch_*.py` de esta carpeta son la historia de cómo se llegó a esa versión. Los documentos los citan como `research/mine/patch_<nombre>.py`, que es donde estaban antes. Calculan la raíz del repo con tres niveles de carpetas (`research/mine/`), así que desde acá escribirían fuera del repo: **no los corras**. Para reproducir la historia, usá `tools/verify_patch_chain.py`, que los copia a una carpeta temporal con la estructura original.

## La última cadena (v4.3 → v4.4)

Se parte de `archive/backups/NQMaster_backup_pre_fillseries.cs` y se aplican en este orden:

| # | Parche | Qué hace | Revisión |
|---|---|---|---|
| 1 | `patch_fillseries.py` | Serie de llenado para el Strategy Analyzer (Off / Tick1 / Second1) | `docs/experimentos/01_*` |
| 2 | `patch_parity_s2.py` | Paridad NT vs. investigación (4 bugs de port) | `docs/experimentos/01_paridad.md` |
| 3 | `patch_clock_check.py` v3 | Control de reloj: plantilla de sesión y horario de verano | `docs/experimentos/revisiones/parches_reloj_riesgo/` |
| 4 | `patch_open_risk.py` v2 | Riesgo abierto a los stops en el panel | ídem |
| 5 | `patch_live_safety.py` v5 | Capa de seguridad en vivo (doble salida, estado de cuenta, aplanado, salidas trabadas…) | `docs/experimentos/revisiones/codigo_2026-10-29/` |
| 6 | `patch_edge_restore.py` v4 | Restauración del monitor de borde | ídem |
| 7 | `patch_panel_risk.py` v2 | Panel de riesgo de la cuenta real | `docs/experimentos/revisiones/panel_2026-10-30/` |

El resultado de la cadena fue idéntico, byte a byte, al `NQMaster.cs` del commit `1ab6aad`: sha256 `85c0a3ef5e6f556dc5870d5ea1aea90b569f5ae17fdd4cfabfc42f97fe84f687`. Después de la consolidación solo se agregó el encabezado de la fuente única.
