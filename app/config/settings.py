import os
from dotenv import load_dotenv

load_dotenv()

class AppConfig:
    PAGE_CONFIG = {
        "page_title": "Психолог | Система записи",
        "page_icon": "🌿",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
    
    # Supabase
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    # anon key (fallback to legacy SUPABASE_KEY for backward compatibility)
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY') or os.getenv('SUPABASE_KEY')
    # service role key for server-side writes (optional but recommended)
    SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
    # legacy field used elsewhere as fallback
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    APP_BASE_URL = os.getenv('APP_BASE_URL', 'http://localhost:8501')
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_ADMIN_CHAT_ID = os.getenv('TELEGRAM_ADMIN_CHAT_ID', '')
    TELEGRAM_BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME', 'Jenyhelperbot')
    
    # Security
    ADMIN_PASSWORD_BCRYPT = os.getenv('ADMIN_PASSWORD_BCRYPT', '')
    ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH', '')
    
    # Features
    TELEGRAM_ENABLED = os.getenv('TELEGRAM_ENABLED', 'true').lower() in ('1', 'true', 'yes')

config = AppConfig()