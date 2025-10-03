# src/collect.py
import argparse
import pandas as pd
from pathlib import Path
from src.utils import sha256_bytes, log_coc

def safe_name(p: str) -> str:
    p = str(p)
    return p.replace("/", "_").rstrip(".") + ".eml"

def run(csv_path: str, out_dir: str, limit: int | None, offset: int, chunksize: int):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    written = 0
    seen = 0

    # stream the CSV in chunks; stop as soon as we hit the limit
    for chunk in pd.read_csv(csv_path, chunksize=chunksize, usecols=["file", "message"]):
        for _, row in chunk.iterrows():
            if seen < offset:
                seen += 1
                continue

            raw_bytes = str(row["message"]).encode("utf-8")
            h = sha256_bytes(raw_bytes)

            out_fp = out / safe_name(row["file"])
            with open(out_fp, "wb") as f:
                f.write(raw_bytes)

            log_coc("COLLECTED", source=row["file"], copied_to=str(out_fp), sha256_raw=h)

            written += 1
            if limit is not None and written >= limit:
                return  # done

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/source/emails.csv")
    ap.add_argument("--out", default="data/raw")
    ap.add_argument("--limit", type=int, default=None, help="Max emails to collect (e.g., 10000)")
    ap.add_argument("--offset", type=int, default=0, help="Skip the first N rows before collecting")
    ap.add_argument("--chunksize", type=int, default=50000, help="CSV read chunk size")
    a = ap.parse_args()
    run(a.csv, a.out, a.limit, a.offset, a.chunksize)

if __name__ == "__main__":
    main()
