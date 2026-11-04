# Campaña y cuenta: lo probado en el programa 5A-5F (27-oct a 4-nov)

Volver a [[00 - MAPA]] · Detalle en `docs/experimentos/` y `docs/ESTADO.md`

El plan es 5 Lucid Flex 150K (6c en la eval, 3c en la fondeada) + 3 MFFU Rapid 50K (1×8). Todo se midió con la función objetivo D1 del programa (`research/mine/objective.py`), sobre los caminos de campaña con costos de $1,90 + 2 ticks por lado, y en los tres casos de edge: completo, −35 % y cero.

## Descartado ❌

- **Tamaño de la eval de Lucid 150K** (exp 03). De 1 a 6 contratos, la regla pre-registrada vuelve a elegir 6c. El trade-off es monótono: más contratos aprueban antes y queman más evals.
- **Umbral de retiro de la Lucid fondeada** (exp 04). De $4.600 a $12.000, ninguno gana condiciones. Queda en $6.000.
- **Presupuesto por plaza, regla 6** (exp 05). Con la revisión trimestral no actúa. Retirada (D2).
- **Escalonar las compras** (diag 06). Las plazas se sincronizan solas en 22-70 días: el plan es una sola cuenta multiplicada.
- **Reglas de pausa 1 y 4** (exp 07). Ninguna protege el primer año. Sin edge, el plan tiene media positiva (+$251 / +$81 por mes en el exp 07; ≈ 0 a +$200 según el exp 10) por la convexidad de los retiros, y se vuelve negativa con menos de medio tick extra de costo. La regla 1 se retiró; la 4 queda como señal de revisión, no como pausa automática (D6).
- **Contratos de Lucid según la volatilidad** (exp 09). Empata en 2020-22 y pierde con −35 %.
- **Repartir los módulos entre plazas** (diag 11). A igual exposición, los quiebres por par de plazas suben ×1,5-6 (×1,2-2 con −35 % y con edge cero). Los módulos casi no se correlacionan (0,03), así que cada plaza ya está diversificada por dentro.
- **Ya estaba descartado antes del programa:**
  - Tope diario por ATR, semanal y mensual (ddlab, 0/40).
  - Tamaño según el colchón ([[Ronda de mejoras 3-oct (techo del sistema)]]).
  - Escalera de MFFU con y sin stop de $1.500 (integración de la ronda 5): con −35 %, P(ganancia) 0,54-0,63.

## Lo que quedó en pie ✅

- **Monitor de borde re-validado con el z corregido** (exp 08). Sin cambio en NinjaTrader: ante la alarma, 252 días sin los módulos de la revisión anual.
- **Estrés de costos** (exp 10).
  - Con el edge completo, el plan aguanta +3 ticks por lado en el bootstrap. Sobre la historia contigua 2023-26, el p10 ya cae con +1 tick.
  - Con −35 %, no tiene margen.
  - Se agregó un umbral de costos al runbook (`slip_model.py`): si el costo real supera al modelado, no hay margen.
- **Capa de seguridad en vivo** (5F). No cambia trades: protege contra doble salida, estado de cuenta desconocido, aplanados fallidos y reinicios del monitor.
- **Panel de riesgo de la cuenta real** (5E). Lotes, tope de riesgo, stops del día y objetivo con la consistencia.

## Sin probar

- Partir las plazas por firma (Lucid = un grupo, MFFU = el otro).
- Perfiles distintos por plaza a 1×. Es una decisión de perfil.
