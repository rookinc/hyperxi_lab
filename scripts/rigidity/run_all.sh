#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../.. && pwd)"
cd "$ROOT"

mkdir -p reports/rigidity/logs

timestamp="$(date +%Y%m%d_%H%M%S)"

echo "== Rigidity pipeline start: ${timestamp} =="

echo
echo "== Phase 1 =="
time python3 scripts/rigidity/phase1_sample_lifts.py \
  | tee "reports/rigidity/logs/phase1_${timestamp}.log"

echo
echo "== Phase 2 =="
time python3 scripts/rigidity/phase2_switch_reduce.py \
  | tee "reports/rigidity/logs/phase2_${timestamp}.log"

echo
echo "== Phase 3 =="
time python3 scripts/rigidity/phase3_aut_reduce.py \
  | tee "reports/rigidity/logs/phase3_${timestamp}.log"

echo
echo "== Rigidity pipeline complete =="
