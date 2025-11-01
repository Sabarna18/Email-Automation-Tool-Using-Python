import os
from pathlib import Path
from dotenv import load_dotenv

# Force load .env from project root (one level up from /src)
ROOT_DIR = Path(__file__).resolve().parent.parent
DOTENV_PATH = ROOT_DIR / ".env.sample"

if DOTENV_PATH.exists():
    load_dotenv(dotenv_path=DOTENV_PATH)
else:
    print(f"⚠️  .env file not found at {DOTENV_PATH}")

def get_env_boolean(key, default=False):
    val = os.environ.get(key, str(default)).lower()
    return val in ("1", "true", "yes", "on")

class Config:
    SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "")
    APP_PASSWORD = os.environ.get("APP_PASSWORD", "")
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    USE_TLS = get_env_boolean("USE_TLS", True)
    DRY_RUN = get_env_boolean("DRY_RUN", False)
    BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "10"))
    BATCH_SLEEP = int(os.environ.get("BATCH_SLEEP", "20"))

config = Config()

if __name__ == "__main__":
    print("Loaded config values:")
    for k in ["SENDER_EMAIL", "APP_PASSWORD", "SMTP_HOST", "SMTP_PORT", "USE_TLS", "DRY_RUN"]:
        print(f"{k} = {getattr(config, k)}")
