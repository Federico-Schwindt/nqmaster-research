#!/usr/bin/env bash
# Tests del repo (frente 5F, 2026-11-04): NinjaScript estatico y con mono, cadena de datos, motores de cuenta y de campana.
# Uso: bash tools/run_tests.sh            (todo, ~5-6 min: incluye el SHA-256 de los datos y la auditoria de PropCycle)
#      bash tools/run_tests.sh --rapido   (sin los lentos, ~30 s: lo minimo antes de commitear un cambio de NQMaster.cs)
# Correr antes de pedir F5 en la PC, junto con bash tools/nt8_stub/check.sh NQMaster.cs. Necesita los datos restaurados
# (bash tools/cloud_setup.sh) y mono / mcs para los tests de C# (si faltan, esos tests se saltean y lo dicen).
set -e
cd "$(dirname "$0")/.."
if [ "$1" = "--rapido" ]; then export NQ_TESTS_RAPIDO=1; fi
python3 -W ignore -m unittest discover -s tests -t . -v
