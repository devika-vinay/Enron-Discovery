# Enron eDiscovery Pipeline

Phases: **Collection → Preservation/Parsing → Normalization → Analysis (NER) → Packaging (DB) → Search**.

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
