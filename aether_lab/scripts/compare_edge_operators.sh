#!/data/data/com.termux/files/usr/bin/bash
set -e

echo
echo "=== ACTUAL COCYCLE / EDGE OPERATOR / NORMALIZED ==="
python aether_lab/scripts/analyze_edge_operator.py \
  --parity-sector-json cocycles/tables/rooted_petrie_parity_sector_table.json \
  --normalize

echo
echo "=== ALL-PLUS / EDGE OPERATOR / NORMALIZED ==="
python aether_lab/scripts/analyze_edge_operator.py \
  --parity-sector-json cocycles/tables/rooted_petrie_allplus_sector_table.json \
  --normalize

echo
echo "=== RANDOMIZED COCYCLE / EDGE OPERATOR / NORMALIZED ==="
python aether_lab/scripts/analyze_edge_operator.py \
  --parity-sector-json cocycles/tables/rooted_petrie_randomized_sector_table.json \
  --normalize
