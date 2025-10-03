#!/usr/bin/env bash
set -euo pipefail
cd /app
export PYTHONPATH=/app

: "${LIMIT:=10000}"

mkdir -p data/source data/raw data/normalized db logs

# Ensure spaCy model exists
python - <<'PY'
import importlib.util
if importlib.util.find_spec("en_core_web_sm") is None:
    import spacy.cli; spacy.cli.download("en_core_web_sm")
PY

# Skipping steps if already done
if [ ! -f data/raw/.collected ]; then
  echo "[1/4] CSV -> raw EML (limit ${LIMIT})"
  python src/collect.py --limit "${LIMIT}"
  touch data/raw/.collected
else echo "[1/4] Skip collect (marker exists)"; fi

if [ ! -f data/normalized/.parsed ]; then
  echo "[2/4] Parse raw -> JSONL"
  python src/parse.py --raw data/raw --out data/normalized
  touch data/normalized/.parsed
else echo "[2/4] Skip parse"; fi

if [ ! -f data/normalized/.normalized ]; then
  echo "[3/4] Normalize"
  python src/normalize.py --inp data/normalized --out data/normalized
  touch data/normalized/.normalized
else echo "[3/4] Skip normalize"; fi

echo "[4/4] Load to target DB"
python src/load.py --inp data/normalized

echo "Starting Streamlit on :8501"
exec streamlit run src/ui_streamlit.py --server.address=0.0.0.0 --server.port=8501
