#!/data/data/com.termux/files/usr/bin/bash
set -e

python aether_lab/scripts/export_rooted_petrie_sectors.py
python aether_lab/scripts/export_rooted_petrie_sectors_allplus.py
python aether_lab/scripts/export_rooted_petrie_sectors_randomized.py

echo
echo "=== ACTUAL COCYCLE / NORMALIZED ==="
python aether_lab/scripts/analyze_signed_sector_operator.py \
  --parity-sector-json cocycles/tables/rooted_petrie_parity_sector_table.json \
  --normalize

echo
echo "=== ALL-PLUS / NORMALIZED ==="
python aether_lab/scripts/analyze_signed_sector_operator.py \
  --parity-sector-json cocycles/tables/rooted_petrie_allplus_sector_table.json \
  --normalize

echo
echo "=== RANDOMIZED COCYCLE / NORMALIZED ==="
python aether_lab/scripts/analyze_signed_sector_operator.py \
  --parity-sector-json cocycles/tables/rooted_petrie_randomized_sector_table.json \
  --normalize
