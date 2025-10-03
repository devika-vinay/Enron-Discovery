import os, json, argparse
from pathlib import Path
import pymysql
from dateutil import parser as dtparser

DDL = """
CREATE TABLE IF NOT EXISTS emails(
  email_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
  file        VARCHAR(255) NOT NULL UNIQUE,
  msg_id      VARCHAR(255),
  from_addr   VARCHAR(320),
  from_name   VARCHAR(255),
  to_addrs    TEXT,
  cc_addrs    TEXT,
  bcc_addrs   TEXT,
  sent_at     DATETIME NULL,
  subject     VARCHAR(512),
  body_text   LONGTEXT,
  body_html   LONGTEXT,
  in_reply_to VARCHAR(255),
  refs        TEXT,
  INDEX idx_from_addr (from_addr),
  INDEX idx_sent_at (sent_at),
  FULLTEXT INDEX ft_subject_body (subject, body_text)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
"""

def to_mysql_dt(s: str | None):
    if not s: return None
    try:
        dt = dtparser.parse(s)
        if dt.tzinfo:
            dt = dt.astimezone(dt.tzinfo).astimezone(tz=None)  # normalize to local-naive
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return None

def get_conn():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST","host.docker.internal"),
        port=int(os.getenv("MYSQL_PORT","3306")),
        user=os.getenv("MYSQL_USER","root"),
        password=os.getenv("MYSQL_PASSWORD",""),
        database=os.getenv("MYSQL_DB","enron-db"),
        charset="utf8mb4",
        autocommit=False,
        cursorclass=pymysql.cursors.Cursor
    )

def main(inp_dir: str):
    conn = get_conn(); cur = conn.cursor()
    cur.execute(DDL); conn.commit()

    files = list(Path(inp_dir).glob("*.jsonl"))
    for fp in files:
        with open(fp, "r", encoding="utf-8") as f:
            rec = json.loads(f.readline())

        sent_at = to_mysql_dt(rec.get("date_utc") or rec.get("date"))
        cur.execute("""
            INSERT INTO emails
              (file,msg_id,from_addr,from_name,to_addrs,cc_addrs,bcc_addrs,
               sent_at,subject,body_text,body_html,in_reply_to,refs)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
              msg_id=VALUES(msg_id),
              from_addr=VALUES(from_addr),
              from_name=VALUES(from_name),
              to_addrs=VALUES(to_addrs),
              cc_addrs=VALUES(cc_addrs),
              bcc_addrs=VALUES(bcc_addrs),
              sent_at=VALUES(sent_at),
              subject=VALUES(subject),
              body_text=VALUES(body_text),
              body_html=VALUES(body_html),
              in_reply_to=VALUES(in_reply_to),
              refs=VALUES(refs)
        """, (
            fp.name,
            rec.get("msg_id",""),
            rec.get("from",""),
            rec.get("from_name",""),
            ",".join(rec.get("to",[])),
            ",".join(rec.get("cc",[])),
            ",".join(rec.get("bcc",[])),
            sent_at,
            rec.get("subject",""),
            rec.get("body_text",""),
            rec.get("body_html",""),
            rec.get("in_reply_to",""),
            ",".join(rec.get("references", rec.get("refs", [])))
        ))
    conn.commit(); conn.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", required=True, help="Directory with normalized JSONL")
    a = ap.parse_args()
    main(a.inp)
