#!/data/data/com.termux/files/usr/bin/bash
set -e

python aether_lab/scripts/export_petrie_holonomy.py
python aether_lab/scripts/export_rooted_petrie_holonomy.py
python aether_lab/scripts/export_rooted_petrie_holonomy_allplus.py

echo
echo "=== PETRIE HOLONOMY REPORT ==="
cat cocycles/tables/petrie_holonomy_report.txt

echo
echo "=== ROOTED PETRIE HOLONOMY REPORT ==="
cat cocycles/tables/rooted_petrie_holonomy_report.txt

echo
echo "=== ROOTED PETRIE HOLONOMY ALL-PLUS REPORT ==="
cat cocycles/tables/rooted_petrie_holonomy_allplus_report.txt
