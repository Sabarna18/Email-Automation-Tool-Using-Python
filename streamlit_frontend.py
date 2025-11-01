import streamlit as st
import pandas as pd
from pathlib import Path
from src.config import config
from src.email_builder import build_message
from src.smtp_client import SMTPClient
from src.logger import logger
from io import StringIO

st.set_page_config(page_title="Email Automation Tool", page_icon="📧", layout="centered")

st.title("📧 Email Automation Tool")
st.write("Send bulk emails easily with attachments, using your Gmail account (App Password required).")

# Sidebar configuration
st.sidebar.header("Configuration")
use_dry_run = st.sidebar.checkbox("Dry Run (Save emails to outbox only)", value=True)

# File upload
st.header("Upload Recipients CSV")
uploaded_csv = st.file_uploader("Upload your recipients CSV", type=["csv"])
if uploaded_csv:
    df = pd.read_csv(uploaded_csv)
    st.dataframe(df.head())

# Compose email
st.header("Compose Email")
subject = st.text_input("Subject", "Hello from Python!")
body = st.text_area("Body", "Dear {name},\n\nThis is a test email.\n\nBest,\nYour Python Script")

# Attachments
st.header("Attachments (optional)")
uploaded_files = st.file_uploader("Upload attachments", type=["pdf", "png", "jpg", "txt", "docx"], accept_multiple_files=True)
attachment_paths = []
if uploaded_files:
    attachment_dir = Path("attachments")
    attachment_dir.mkdir(exist_ok=True)
    for file in uploaded_files:
        save_path = attachment_dir / file.name
        with open(save_path, "wb") as f:
            f.write(file.read())
        attachment_paths.append(str(save_path))
    st.success(f"Uploaded {len(uploaded_files)} attachments.")

# Send button
if st.button("🚀 Send Emails"):
    if not uploaded_csv:
        st.error("Please upload a recipients CSV first.")
    else:
        st.info("Sending emails... Please wait.")
        smtp_client = None
        try:
            smtp_client = SMTPClient()
            smtp_client.connect()

            sent_count = 0
            for idx, row in df.iterrows():
                msg = build_message(config.SENDER_EMAIL, {
                    "email": row["email"],
                    "name": row.get("name", "User"),
                    "subject": subject,
                    "body": body,
                    "attachments": attachment_paths,
                })
                if use_dry_run:
                    outbox = Path("outbox")
                    outbox.mkdir(exist_ok=True)
                    file_name = outbox / f"{idx:03d}_{row['email'].replace('@','_at_')}.eml"
                    with open(file_name, "wb") as f:
                        f.write(msg.as_bytes())
                else:
                    smtp_client.send_message(msg)
                    sent_count += 1
                    st.write(f"✅ Sent to {row['email']}")

            st.success(f"Done! {sent_count} emails sent successfully.")
        except Exception as e:
            st.error(f"Error occurred: {e}")
        finally:
            if smtp_client:
                smtp_client.quit()
