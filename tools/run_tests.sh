#!/usr/bin/env bash
# Tests del repo (frente 5F, 2026-11-04): NinjaScript estatico y con mono, cadena de datos, motores de cuenta y de campana.
# Uso: bash tools/run_tests.sh            (todo: ~40 s con el disco en cache, ~5 min en frio por el SHA-256 de los datos)
#      bash tools/run_tests.sh --rapido   (sin el SHA-256 de los datos, ~35 s: lo minimo antes de commitear un cambio de NQMaster.cs)
# Correr antes de pedir F5 en la PC, junto con bash tools/nt8_stub/check.sh NQMaster.cs. Necesita los datos restaurados
# (bash tools/cloud_setup.sh) y mono / mcs: sin ellos se saltearia justo lo que importa antes de un F5, asi que el script se niega
# salvo con NQ_TESTS_SIN_MONO=1 (y entonces lo dice).
set -e
cd "$(dirname "$0")/.."
if [ "$1" = "--rapido" ]; then export NQ_TESTS_RAPIDO=1; fi
if ! command -v mcs >/dev/null || ! command -v mono >/dev/null; then
  if [ "$NQ_TESTS_SIN_MONO" != "1" ]; then
    echo "Faltan mcs / mono (apt-get install -y mono-mcs mono-runtime): sin ellos no corren el type-check, la regla de horario de verano,"
    echo "EdgeParse ni PropCycle. Para correr igual el resto: NQ_TESTS_SIN_MONO=1 bash tools/run_tests.sh"; exit 2
  fi
  echo "AVISO: sin mono / mcs: se saltean los tests de C# (no alcanza para pedir F5)"
fi
python3 -W ignore -m unittest discover -s tests -t . -v
