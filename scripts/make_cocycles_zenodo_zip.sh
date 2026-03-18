#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="$HOME/dev/cori/aether"
SRC_DIR="$ROOT/cocycles"
DEFAULT_OUT_DIR="$ROOT/output"

# Accept either:
#   ./script.sh
#   ./script.sh myzip.zip
#   ./script.sh output/myzip.zip
OUT_ARG="${1:-cocycles_zenodo.zip}"

if [ ! -d "$SRC_DIR" ]; then
  echo "Missing source directory: $SRC_DIR" >&2
  exit 1
fi

mkdir -p "$DEFAULT_OUT_DIR"

case "$OUT_ARG" in
  /*) OUT_PATH="$OUT_ARG" ;;
  */*) OUT_PATH="$ROOT/$OUT_ARG" ;;
  *) OUT_PATH="$DEFAULT_OUT_DIR/$OUT_ARG" ;;
esac

OUT_DIR="$(dirname "$OUT_PATH")"
mkdir -p "$OUT_DIR"

cd "$ROOT"

rm -f "$OUT_PATH"

zip -r "$OUT_PATH" "cocycles" \
  -x "*.aux" "*.log" "*.out" "*.toc" "*.bbl" "*.blg" \
     "*.fdb_latexmk" "*.fls" "*.synctex.gz" "*.DS_Store" \
     "*.git/*" "*/__pycache__/*"

echo
echo "Created: $OUT_PATH"
echo
echo "Archive contents preview:"
unzip -l "$OUT_PATH" | sed -n '1,40p'
