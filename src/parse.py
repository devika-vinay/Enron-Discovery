import argparse, json
from pathlib import Path
from mailparser import parse_from_file
from src.utils import sha256_file, log_coc

def parse_email_file(fp: Path):
    mail = parse_from_file(str(fp))
    return {
        "file": str(fp),
        "msg_id": mail.message_id or "",
        "from": mail.from_[0][1] if mail.from_ else "",
        "from_name": mail.from_[0][0] if mail.from_ else "",
        "to": [x[1] for x in mail.to] if mail.to else [],
        "cc": [x[1] for x in mail.cc] if mail.cc else [],
        "bcc": [x[1] for x in mail.bcc] if mail.bcc else [],
        "subject": mail.subject or "",
        "date": mail.date.replace(tzinfo=None).isoformat() if mail.date else "",
        "body_text": mail.text_plain[0] if mail.text_plain else "",
        "body_html": mail.body if mail.body else "",
        "in_reply_to": mail.in_reply_to or "",
        "references": mail.references or [],
        "attachments": [{"filename": a["filename"], "mail_content_type": a["mail_content_type"]} for a in mail.attachments]
    }

def main(raw_dir: str, out_dir: str):
    raw = Path(raw_dir); out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for fp in raw.iterdir():
        if fp.is_file():
            rec = parse_email_file(fp)
            out_fp = out / (fp.stem + ".jsonl")
            with open(out_fp, "w", encoding="utf-8") as f:
                f.write(json.dumps(rec) + "\n")
            log_coc("PRESERVED",
                    source=str(fp),
                    normalized=str(out_fp),
                    sha256_raw=sha256_file(str(fp)))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    main(a.raw, a.out)
