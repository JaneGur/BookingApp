import streamlit as st
from models.settings import SystemSettings
from core.database import db_manager
from config.constants import DEFAULT_SETTINGS

class SettingsService:
    def __init__(self):
        self.supabase = db_manager.get_client()
    
    @st.cache_data(ttl=300)
    def get_settings(_self) -> SystemSettings:
        """Получение настроек системы"""
        try:
            response = _self.supabase.table('settings').select('*').eq('id', 1).execute()
            if response.data:
                settings_data = response.data[0]
                return SystemSettings.from_dict(settings_data)
            else:
                # Создаем настройки по умолчанию
                try:
                    _self.supabase.table('settings').insert({**DEFAULT_SETTINGS, 'id': 1}).execute()
                    return SystemSettings.from_dict(DEFAULT_SETTINGS)
                except Exception as insert_error:
                    # Если не удалось вставить все поля, пробуем только основные
                    basic_settings = {
                        'work_start': '09:00',
                        'work_end': '18:00', 
                        'session_duration': 60,
                        'break_duration': 15
                    }
                    _self.supabase.table('settings').insert({**basic_settings, 'id': 1}).execute()
                    return SystemSettings.from_dict({**basic_settings, **DEFAULT_SETTINGS})
                    
        except Exception as e:
            print(f"❌ Ошибка получения настроек: {e}")
            # Возвращаем настройки по умолчанию
            return SystemSettings.from_dict(DEFAULT_SETTINGS)
    
    def update_settings(self, settings_data: dict) -> bool:
        """Обновление настроек системы"""
        try:
            # Получаем текущие настройки
            current_settings = self.get_settings()
            
            # Обновляем только существующие поля
            update_data = {}
            for key, value in settings_data.items():
                if hasattr(current_settings, key):
                    update_data[key] = value
            
            if update_data:
                self.supabase.table('settings').update(update_data).eq('id', 1).execute()
                st.cache_data.clear()
                return True
            else:
                return False
        except Exception as e:
            print(f"❌ Ошибка обновления настроек: {e}")
            return False