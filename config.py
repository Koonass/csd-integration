"""
Configuration settings for CSD Portal Integration
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Database settings
DATABASE_PATH = BASE_DIR / 'submissions.db'

# Logging settings
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'submissions.log'
LOG_LEVEL = 'INFO'

# CSD Portal settings
CSD_PORTAL_URL = 'https://www.csdportal.com/isDesignCenter/?loc=2378'
CSD_SUBMISSION_TIMEOUT = 30  # seconds

# JotForm settings
JOTFORM_WEBHOOK_SECRET = os.environ.get('JOTFORM_WEBHOOK_SECRET', '')

# Field mapping file
FIELD_MAPPING_FILE = BASE_DIR / 'field_mapping.json'

# Retry settings
MAX_RETRIES = 2
RETRY_DELAY = 5  # seconds

# Email notification settings (for future use)
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', '')
SMTP_SERVER = os.environ.get('SMTP_SERVER', '')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))

# Flask settings
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
