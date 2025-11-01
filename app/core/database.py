import streamlit as st
from supabase import create_client, Client
from config.settings import config

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.supabase = None
            self._initialized = True
    
    @st.cache_resource
    def get_client(_self) -> Client:
        """Клиент Supabase для публичных операций (anon).
        Fallback на SUPABASE_KEY для обратной совместимости."""
        try:
            url = getattr(config, 'SUPABASE_URL', None)
            anon_key = getattr(config, 'SUPABASE_ANON_KEY', None) or getattr(config, 'SUPABASE_KEY', None)
            if not url or not anon_key:
                st.error("❌ SUPABASE_URL и SUPABASE_ANON_KEY (или SUPABASE_KEY) не настроены")
                return None
            client = create_client(url, anon_key)
            _self.supabase = client
            return client
        except Exception as e:
            st.error(f"❌ Ошибка подключения к Supabase (anon): {e}")
            return None

    @st.cache_resource
    def get_service_client(_self) -> Client:
        """Клиент Supabase с сервисным ключом для админских операций (обходит RLS)."""
        try:
            url = getattr(config, 'SUPABASE_URL', None)
            svc_key = getattr(config, 'SUPABASE_SERVICE_ROLE_KEY', None)
            if not url or not svc_key:
                st.error("❌ SUPABASE_SERVICE_ROLE_KEY не настроен. Админские операции записи будут недоступны.")
                return None
            return create_client(url, svc_key)
        except Exception as e:
            st.error(f"❌ Ошибка подключения к Supabase (service): {e}")
            return None
    
    def init_auth_table(self) -> bool:
        """Инициализация таблицы аутентификации"""
        try:
            self.supabase.table('client_auth').select('phone_hash').limit(1).execute()
            return True
            
        except Exception as e:
            st.error(f"❌ Таблица client_auth не найдена или недоступна. Ошибка: {e}")
            st.markdown("""
            ### 🔧 Решение проблемы:
            
            1. **Создайте таблицу client_auth в Supabase:**
            ```sql
            CREATE TABLE IF NOT EXISTS client_auth (
                phone_hash TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            ```
            
            2. **Рекомендуемые индексы и ограничения для записей:**
            ```sql
            CREATE UNIQUE INDEX IF NOT EXISTS bookings_unique_slot ON bookings(booking_date, booking_time) WHERE status <> 'cancelled';
            CREATE INDEX IF NOT EXISTS bookings_phone_idx ON bookings(phone_hash);
            ```
            
            3. **Перезапустите приложение после миграции схемы**
            """)
            return False

# Синглтон для работы с базой
db_manager = DatabaseManager()