# Enron eDiscovery Pipeline
A lightweight, end-to-end eDiscovery demo that ingests the Enron emails CSV, preserves raw evidence, normalizes, loads into a queryable store, and serves a simple Streamlit UI for search & review.
```

- Chain of Custody: every step appends a JSONL record in `logs/coc.jsonl` with hashes & timestamps.
- Data: place source `.mbox` / `.eml` in `data/source/`
```bash
make setup
make collect
make parse
make normalize
make ner
make load
python src/search_cli.py search --contains "California"
