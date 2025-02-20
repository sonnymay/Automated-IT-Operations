import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Base paths
PROJECT_ROOT = Path(__file__).parent
CATALOG_DIR = PROJECT_ROOT / "catalog_files"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOG_FILE = PROJECT_ROOT / "automation.log"

# Create required directories
CATALOG_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Email configuration using environment variables
EMAIL_CONFIG = {
    "sender": os.getenv("AUTOMATION_EMAIL_SENDER", "your_email@example.com"),
    "recipient": os.getenv("AUTOMATION_EMAIL_RECIPIENT", "recipient@example.com"),
    "smtp_server": os.getenv("AUTOMATION_SMTP_SERVER", "smtp.example.com"),
    "smtp_port": int(os.getenv("AUTOMATION_SMTP_PORT", "587")),
    "username": os.getenv("AUTOMATION_EMAIL_USERNAME", "your_username"),
    "password": os.getenv("AUTOMATION_EMAIL_PASSWORD", "your_password")
}

# System health thresholds
HEALTH_THRESHOLDS = {
    "cpu_warning": 80,
    "disk_warning": 90,
    "memory_warning": 90
}
