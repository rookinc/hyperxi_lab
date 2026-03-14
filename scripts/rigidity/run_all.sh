#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../.. && pwd)"
cd "$ROOT"

mkdir -p reports/rigidity/logs

timestamp="$(date +%Y%m%d_%H%M%S)"

echo "============================================================"
echo "HyperXi Rigidity Pipeline"
echo "Start time: $(date)"
echo "============================================================"

echo
echo "================ PHASE 1 ================="
echo "Full enumeration of 14/16 signings"
echo

time python3 scripts/rigidity/phase1_sample_lifts.py \
| tee "reports/rigidity/logs/phase1_${timestamp}.log"

echo
echo "================ PHASE 2 ================="
echo "Switching reduction"
echo

time python3 scripts/rigidity/phase2_switch_reduce.py \
| tee "reports/rigidity/logs/phase2_${timestamp}.log"

echo
echo "================ PHASE 3 ================="
echo "Automorphism + switching reduction"
echo

time python3 scripts/rigidity/phase3_aut_reduce.py \
| tee "reports/rigidity/logs/phase3_${timestamp}.log"

echo
echo "============================================================"
echo "Rigidity pipeline complete"
echo "Finish time: $(date)"
echo "============================================================"

