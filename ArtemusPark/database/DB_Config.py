import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "artemus_db"),
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
    "autocommit": True,
    "raise_on_warnings": True,
}

# Admin connection config (without database) for initialization
ADMIN_DB_CONFIG = {
    "host": DB_CONFIG["host"],
    "port": DB_CONFIG["port"],
    "user": DB_CONFIG["user"],
    "password": DB_CONFIG["password"],
    "charset": DB_CONFIG["charset"],
    "collation": DB_CONFIG["collation"],
    "autocommit": True,
    "raise_on_warnings": True,
}
