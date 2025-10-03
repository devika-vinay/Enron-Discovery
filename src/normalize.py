import argparse, json, re
from pathlib import Path
from datetime import datetime, timezone

def clean_text(t: str) -> str:
    if not t: return ""
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

def iso_utc(ts: str) -> str:
    if not ts: return ""
    try:
        dt = datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except Exception:
        return ts

def main(inp: str, out: str):
    inp_p, out_p = Path(inp), Path(out)
    for fp in inp_p.glob("*.jsonl"):
        with open(fp, "r", encoding="utf-8") as f:
            rec = json.loads(f.readline())
        rec["body_text"] = clean_text(rec.get("body_text", ""))
        rec["subject"] = clean_text(rec.get("subject", ""))
        rec["date_utc"] = iso_utc(rec.get("date", ""))
        with open(fp, "w", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    main(a.inp, a.out)
