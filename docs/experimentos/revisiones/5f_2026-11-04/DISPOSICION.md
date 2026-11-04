# Disposición de la revisión del frente 5F (fuente única y tests, 4-nov)

El informe del revisor está tal cual en `revision_5f.md`. **Veredicto: listo para main, sin bloqueos.** La consolidación es exacta y los 15 tests pasan sin escribir en el repo. El revisor corrió 38 mutaciones.

| Hallazgo | Severidad | Qué se hizo |
|---|---|---|
| El README de `archive/patches` da una razón falsa | Media | **Corregido:** desde `archive/patches/` los parches llegan igual a la raíz del repo. Hoy los frenan sus guardas, pero algunos escriben backups en la raíz. El README sigue diciendo que no se corran y explica que las guardas que mandan a "ver docs/ESTADO.md" se refieren a esa receta. |
| Sin mono, la batería da verde | Media | **Corregido:** `tools/run_tests.sh` sale con error si faltan `mcs` o `mono`, salvo con `NQ_TESTS_SIN_MONO=1`, y en ese caso lo avisa. |
| El stub con `Indicator : StrategyBase` oculta usos de miembros de estrategia en un indicador | Media/Baja | **Corregido:** el stub tiene una base común `NinjaScriptBase`, y `StrategyBase` e `Indicator` heredan de ella por separado. Los indicadores ya no ven `EnterLong`, `Position`, `SetStopLoss` y demás. Los 4 `.cs` siguen type-checkeando. |
| El regex de palabras contextuales tiene huecos | Baja | **Corregido:** se agregó un test por reflexión sobre el ensamblado compilado contra el stub; se excluyen los accesores de propiedades. Ve métodos, constructores, lambdas y delegados. El regex queda como respaldo. La mutación de una lambda con un parámetro `when` la detecta el test nuevo. |
| `fmtcheck` solo cuenta argumentos | Baja | **Corregido:** valida la sintaxis del formato (llaves balanceadas, items `{n[,ancho][:formato]}`) y también revisa `String.Format` y `.AppendFormat`. Las mutaciones `{0 y`, `{0}} z` y `{1}` con 1 argumento se detectan. |
| `test_status_translations` tiene puntos ciegos | Baja | **Corregido:** toma todos los literales del lado derecho de `status = …` (ternarios, `string.Format`, sin espacios). Una concatenación traducida por su prefijo (baja volatilidad) y los literales ya en castellano no cuentan. La mutación de un ternario en inglés se detecta. |
| `test_us_dst_rule` muestrea hora por hora | Baja | **Corregido:** muestrea cada 15 minutos. |
| `--rapido` deja afuera PropCycle | Baja | **Corregido:** PropCycle corre también en `--rapido`; solo queda afuera el SHA-256 de los datos. |
| La huella de `research_set` depende de los datos de oro y del orden de filas | Info | **Documentado** en el test, que también pide los datos de oro con un mensaje claro. |
| Falta un caso de `fb` negativo en `test_edge_parse` | Info | **Agregado** (12 casos). |
| `test_patch_chain_history` y el del encabezado no protegen el archivo actual | Info | Sin cambio. Son controles de la historia y de la consolidación; está dicho en sus docstrings. |
| El comentario del renombre en `NQAccountGuard.cs` | OK | **Suavizado:** `on` es una palabra contextual de LINQ; la evidencia de NinjaTrader es `when` (17-oct). |
| Detalles de los docs | Baja | **Corregido:** "el estado inicial más 52 cambios"; las rutas vivas de ESTADO pasan a `archive/patches/`; el encabezado de `NQMaster.cs` dice "ICT (x1 since 2026-10-27)"; la nota de Obsidian precisa la media sin edge (exp 07 / exp 10) y que lo de +3 ticks vale en el bootstrap. |

Verificación final: `bash tools/run_tests.sh` da 16/16 OK en 42 s, y `check.sh` da 0 en los 4 `.cs`. Las tres mutaciones nuevas (una lambda con `when`, un ternario en inglés y un formato roto) se probaron en una copia y las detectan los tests.
