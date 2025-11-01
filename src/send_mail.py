import csv
import argparse
import time
from pathlib import Path
from email import policy
from email.generator import BytesGenerator
from io import BytesIO

# Local imports
from .config import config
from .logger import logger
from .email_builder import build_message
from .smtp_client import SMTPClient


# === Directories ===
OUTBOX_DIR = Path("outbox")
OUTBOX_DIR.mkdir(exist_ok=True)


# === Utility Functions ===
def save_eml(msg, filename: Path):
    """Save EmailMessage to a .eml file for inspection (dry-run)."""
    buf = BytesIO()
    gen = BytesGenerator(buf, policy=policy.default)
    gen.flatten(msg)
    filename.write_bytes(buf.getvalue())
    logger.info("Saved EML to %s", filename)


def read_recipients(csv_path: Path):
    """Yield each recipient's info from a CSV file."""
    with csv_path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


# === Core Sending Function ===
def send_all(csv_path: Path, dry_run: bool):
    """Send (or simulate sending) emails to all recipients in CSV."""
    recipients = list(read_recipients(csv_path))
    total = len(recipients)
    logger.info("Loaded %d recipients from %s", total, csv_path)

    # Log dry run status clearly
    if dry_run:
        logger.warning("DRY_RUN is enabled → emails will NOT be sent. They’ll be saved in outbox/.")
    else:
        logger.info("DRY_RUN disabled → emails WILL be sent via SMTP.")

    # Connect to SMTP if not dry run
    smtp_client = None
    if not dry_run:
        smtp_client = SMTPClient()
        smtp_client.connect()

    try:
        sent_count = 0

        for idx, row in enumerate(recipients, start=1):
            try:
                msg = build_message(config.SENDER_EMAIL, row)

                if dry_run:
                    # Save locally
                    safe_email = row.get("email", "unknown").replace("@", "_at_")
                    out_file = OUTBOX_DIR / f"{idx:03d}_{safe_email}.eml"
                    save_eml(msg, out_file)
                else:
                    # Actually send
                    smtp_client.send_message(msg)
                    logger.info("✅ Sent (%d/%d) to %s", idx, total, row.get("email"))
                    sent_count += 1

                # Optional batching (avoid Gmail rate limits)
                if idx % config.BATCH_SIZE == 0:
                    logger.info("Batch sent: %d messages. Sleeping %s seconds...", idx, config.BATCH_SLEEP)
                    time.sleep(config.BATCH_SLEEP)

            except Exception as e:
                logger.exception("❌ Failed to process recipient %s: %s", row.get("email"), e)

        logger.info("✅ Done. Sent: %d / %d total", sent_count, total)

    finally:
        if smtp_client:
            smtp_client.quit()


# === CLI Entry Point ===
def main():
    parser = argparse.ArgumentParser(description="Email Automation Tool (Intermediate Level)")
    parser.add_argument("--csv", required=True, help="Path to recipients CSV file")
    parser.add_argument("--dry-run", action="store_true", help="Simulate emails (save to outbox instead of sending)")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        logger.error("CSV file not found: %s", csv_path)
        return

    # --- FIXED LOGIC HERE ---
    # Priority: CLI argument overrides .env setting
    dry_run = args.dry_run if args.dry_run else config.DRY_RUN
    logger.info("Config.DRY_RUN = %s | CLI flag = %s → Using dry_run = %s", config.DRY_RUN, args.dry_run, dry_run)

    send_all(csv_path, dry_run=dry_run)


if __name__ == "__main__":
    main()
