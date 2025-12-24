import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Telegram Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN không được tìm thấy trong file .env")

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///accounting.db')

# OCR Configuration
OCR_TYPE = os.getenv('OCR_TYPE', 'easyocr')
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# AI/LLM Configuration
AI_PROVIDER = os.getenv('AI_PROVIDER', 'gemini')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Application Settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 20))
TEMP_FILE_RETENTION_HOURS = int(os.getenv('TEMP_FILE_RETENTION_HOURS', 24))

# Directories
DATA_DIR = BASE_DIR / 'data'
TEMPLATES_DIR = BASE_DIR / 'templates'
DATA_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

# OCR Languages
OCR_LANGUAGES = ['vi', 'en']  # Vietnamese and English

# Validation
if AI_PROVIDER == 'gemini' and not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY không được tìm thấy trong file .env")
elif AI_PROVIDER == 'openai' and not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY không được tìm thấy trong file .env")
