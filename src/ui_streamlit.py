import os
import datetime as dt
import pandas as pd
import pymysql
import streamlit as st

@st.cache_resource
def get_conn():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "host.docker.internal"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "enron"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DB", "enron-db"),
        charset="utf8mb4",
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )

def run_search(q, sender, after, before, limit):
    conn = get_conn(); cur = conn.cursor()
    where, params = [], []

    if sender:
        where.append("e.from_addr LIKE %s")
        params.append(f"%{sender}%")
    if after:
        where.append("DATE(e.sent_at) >= %s")
        params.append(after)
    if before:
        where.append("DATE(e.sent_at) <= %s")
        params.append(before)

    if q:
        sql = """
        SELECT e.email_id, e.sent_at, e.from_addr, e.subject
        FROM emails e
        WHERE MATCH(e.subject, e.body_text) AGAINST (%s IN NATURAL LANGUAGE MODE)
        """
        params = [q] + params
        if where: sql += " AND " + " AND ".join(where)
        sql += " ORDER BY e.sent_at LIMIT %s"
    else:
        sql = "SELECT e.email_id, e.sent_at, e.from_addr, e.subject FROM emails e"
        if where: sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY e.sent_at LIMIT %s"

    params.append(limit)
    cur.execute(sql, params)
    rows = cur.fetchall()
    return pd.DataFrame(rows)

def fetch_email(email_id: int):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""
        SELECT email_id, file, msg_id, from_addr, from_name, to_addrs, cc_addrs, bcc_addrs,
               sent_at, subject, body_text, body_html, in_reply_to, refs
        FROM emails WHERE email_id=%s
    """, (email_id,))
    return cur.fetchone()

# ---------------- UI ----------------
st.set_page_config(page_title="Enron eDiscovery", layout="wide")
st.title("Enron eDiscovery – Search (MySQL)")

with st.sidebar:
    st.subheader("Filters")
    q = st.text_input("Full-text (e.g., California)")
    sender = st.text_input("From contains")
    c1, c2 = st.columns(2)
    with c1:
        after = st.date_input("After", value=None)
    with c2:
        before = st.date_input("Before", value=None)
    limit = st.select_slider("Limit", options=[25, 50, 100, 200], value=50)
    do_search = st.button("Search")

if do_search:
    df = run_search(
        q.strip() or None,
        sender.strip() or None,
        after.isoformat() if isinstance(after, dt.date) else None,
        before.isoformat() if isinstance(before, dt.date) else None,
        int(limit),
    )
    st.caption(f"{len(df)} result(s)")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.download_button("Download CSV", data=df.to_csv(index=False), file_name="results.csv")
        # Selection to view a specific email
        email_id = st.selectbox("Open message", options=df["email_id"].tolist())
        if st.button("View"):
            rec = fetch_email(int(email_id))
            if rec:
                st.markdown(f"### {rec['subject'] or '(no subject)'}")
                st.caption(f"ID {rec['email_id']} • File {rec['file']} • Sent {rec['sent_at']}")
                meta_cols = st.columns(2)
                with meta_cols[0]:
                    st.write(f"**From:** {rec['from_addr']} ({rec['from_name'] or ''})")
                    st.write(f"**To:** {rec['to_addrs']}")
                    st.write(f"**CC:** {rec['cc_addrs']}")
                with meta_cols[1]:
                    st.write(f"**BCC:** {rec['bcc_addrs']}")
                    st.write(f"**In-Reply-To:** {rec['in_reply_to']}")
                st.divider()
                st.subheader("Body (text)")
                st.write(rec["body_text"] or "(empty)")
            else:
                st.warning("Email not found.")
    else:
        st.info("No results.")
else:
    st.info("Set filters and click **Search** to begin.")
