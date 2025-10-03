# Enron eDiscovery Pipeline

## Highlights

A lightweight, end-to-end eDiscovery pipelin that ingests the Enron emails CSV, preserves raw evidence, normalizes, loads into a queryable store, and serves a simple Streamlit UI for search & review.

- ETL pipeline: Collect -> Parse -> Normalize -> Load → Search UI
- Chain of custody: SHA-256 fingerprints + JSONL audit log
- Search UI: Streamlit app with full-text search, sender & date filters, CSV export
---

---
## Pipeline Stages (what each script does)

### 1) Collect.py
- Streams the CSV in chunks
- Writes each message as UTF-8 bytes to data/raw/
- Computes SHA-256 of the raw bytes and logs it to logs/coc.jsonl for integrity. If any byte changes, the hash changes.

### 2) Parse.py
- Extracts headers (Message-ID, Date, From, To, Subject, etc.) and body (text/plain, text/html).
- Saves one .jsonl record per email in data/normalized/.

### 3) Normalize.py 
- Lowercases/strips addresses, normalizes date to ISO if possible, removes obvious noise.
- Preps records for search.

### 5) Load.py
- Creates emails table (DDL below)
```
CREATE TABLE IF NOT EXISTS emails (
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
)
```
---

---
## Quickstart

### Prereqs
- Install Docker Desktop.
- Have MySQL running on Windows/mac host
- Use the Kaggle Enron Emails CSV and save as: data/source/emails.csv
- Create .env (project root) and paste the following
```
MYSQL_HOST=host.docker.internal
MYSQL_PORT=3306
MYSQL_DB=enron-db
MYSQL_USER="your username"
MYSQL_PASSWORD="your password"
```

### Running the pipeline (commands to be executed on cmd)
```
docker build -t enron-ediscovery:latest .
docker compose up --build
```
---

---
## Roadmap Ideas
- Entity browser (PERSON/ORG filters) in the UI
- Attachment extraction
- PII redaction
- RAG summaries
---
