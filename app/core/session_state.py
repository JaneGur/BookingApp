import streamlit as st
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class SessionState:
    """Класс для управления состоянием сессии"""
    # Статусы аутентификации
    admin_logged_in: bool = False
    client_logged_in: bool = False
    client_phone: str = ""
    client_name: str = ""
    
    # Навигация и UI
    current_tab: str = "Запись"
    show_admin_login: bool = False
    selected_time: Optional[str] = None
    booking_date: Optional[str] = None
    
    # Управление клиентами (админ)
    selected_client: Optional[str] = None
    selected_client_name: Optional[str] = None
    show_new_booking_form: bool = False
    show_stats: bool = False
    confirm_delete: Dict[str, Any] = None
    search_query: str = ''
    auto_refresh: bool = False
    
    # Формы аутентификации
    show_client_login: bool = False
    show_client_registration: bool = False
    show_password_reset: bool = False
    show_password_reset_public: bool = False  # НОВОЕ ПОЛЕ
    registration_phone: str = ''
    registration_name: str = ''
    
    # Системные флаги
    auth_table_initialized: bool = False

def init_session_state():
    """Инициализация всех переменных session state"""
    defaults = SessionState()
    defaults.confirm_delete = {}
    
    for key, value in defaults.__dict__.items():
        if key not in st.session_state:
            st.session_state[key] = value

def client_login(phone: str, name: str):
    """Вход клиента в систему"""
    st.session_state.client_logged_in = True
    st.session_state.client_phone = phone
    st.session_state.client_name = name
    st.session_state.current_tab = "🏠 Главная"
    
    # Сбрасываем флаги форм
    st.session_state.show_client_login = False
    st.session_state.show_client_registration = False
    st.session_state.show_password_reset = False

def client_logout():
    """Выход клиента из системы"""
    st.session_state.client_logged_in = False
    st.session_state.client_phone = ""
    st.session_state.client_name = ""
    st.session_state.current_tab = "Запись"
    
    # Сбрасываем связанные состояния
    st.session_state.selected_time = None
    st.session_state.booking_date = None

def admin_login():
    """Вход администратора в систему"""
    st.session_state.admin_logged_in = True
    st.session_state.show_admin_login = False

def admin_logout():
    """Выход администратора из системы"""
    st.session_state.admin_logged_in = False
    
    # Сбрасываем состояния админ-панели
    st.session_state.selected_client = None
    st.session_state.selected_client_name = None
    st.session_state.show_new_booking_form = False
    st.session_state.show_stats = False
    st.session_state.search_query = ''

def show_client_auth_forms():
    """Показать формы аутентификации клиента"""
    st.session_state.show_client_login = True
    st.session_state.show_client_registration = False
    st.session_state.show_password_reset = False
    st.session_state.show_admin_login = False

def show_client_registration():
    """Показать форму регистрации клиента"""
    st.session_state.show_client_login = False
    st.session_state.show_client_registration = True
    st.session_state.show_password_reset = False
    st.session_state.show_admin_login = False

def show_password_reset():
    """Показать форму сброса пароля"""
    st.session_state.show_client_login = False
    st.session_state.show_client_registration = False
    st.session_state.show_password_reset = True
    st.session_state.show_admin_login = False

def show_admin_login():
    """Показать форму входа администратора"""
    st.session_state.show_client_login = False
    st.session_state.show_client_registration = False
    st.session_state.show_password_reset = False
    st.session_state.show_admin_login = True

def hide_all_forms():
    """Скрыть все формы аутентификации"""
    st.session_state.show_client_login = False
    st.session_state.show_client_registration = False
    st.session_state.show_password_reset = False
    st.session_state.show_admin_login = False

def set_current_tab(tab_name: str):
    """Установить текущую вкладку"""
    st.session_state.current_tab = tab_name

def set_selected_time(time_slot: str):
    """Установить выбранное время"""
    st.session_state.selected_time = time_slot

def clear_selected_time():
    """Очистить выбранное время"""
    st.session_state.selected_time = None

def set_booking_date(date: str):
    """Установить выбранную дату"""
    st.session_state.booking_date = date

def set_selected_client(client_hash: str, client_name: str):
    """Установить выбранного клиента (для админа)"""
    st.session_state.selected_client = client_hash
    st.session_state.selected_client_name = client_name

def clear_selected_client():
    """Очистить выбранного клиента"""
    st.session_state.selected_client = None
    st.session_state.selected_client_name = None

def toggle_new_booking_form():
    """Переключить отображение формы новой записи"""
    st.session_state.show_new_booking_form = not st.session_state.get('show_new_booking_form', False)

def toggle_stats():
    """Переключить отображение статистики"""
    st.session_state.show_stats = not st.session_state.get('show_stats', False)

def set_search_query(query: str):
    """Установить поисковый запрос"""
    st.session_state.search_query = query

def clear_search_query():
    """Очистить поисковый запрос"""
    st.session_state.search_query = ''

def set_registration_data(phone: str, name: str):
    """Установить данные для регистрации"""
    st.session_state.registration_phone = phone
    st.session_state.registration_name = name

def clear_registration_data():
    """Очистить данные регистрации"""
    st.session_state.registration_phone = ''
    st.session_state.registration_name = ''

def mark_auth_table_initialized():
    """Пометить таблицу аутентификации как инициализированную"""
    st.session_state.auth_table_initialized = True

def is_auth_table_initialized() -> bool:
    """Проверить, инициализирована ли таблица аутентификации"""
    return st.session_state.get('auth_table_initialized', False)

def get_client_session() -> Dict[str, Any]:
    """Получить данные сессии клиента"""
    return {
        'logged_in': st.session_state.client_logged_in,
        'phone': st.session_state.client_phone,
        'name': st.session_state.client_name
    }

def get_admin_session() -> Dict[str, Any]:
    """Получить данные сессии администратора"""
    return {
        'logged_in': st.session_state.admin_logged_in
    }

def get_ui_state() -> Dict[str, Any]:
    """Получить состояние UI"""
    return {
        'current_tab': st.session_state.current_tab,
        'selected_time': st.session_state.selected_time,
        'booking_date': st.session_state.booking_date,
        'search_query': st.session_state.search_query,
        'show_stats': st.session_state.show_stats
    }

def reset_ui_state():
    """Сбросить состояние UI к значениям по умолчанию"""
    st.session_state.current_tab = "Запись"
    st.session_state.selected_time = None
    st.session_state.booking_date = None
    st.session_state.search_query = ''
    st.session_state.show_stats = False
    st.session_state.show_new_booking_form = False

def is_any_form_visible() -> bool:
    """Проверить, видна ли какая-либо форма аутентификации"""
    return (st.session_state.show_client_login or 
            st.session_state.show_client_registration or 
            st.session_state.show_password_reset or 
            st.session_state.show_admin_login)

def clear_all_temp_data():
    """Очистить все временные данные"""
    st.session_state.selected_time = None
    st.session_state.booking_date = None
    st.session_state.selected_client = None
    st.session_state.selected_client_name = None
    st.session_state.search_query = ''
    st.session_state.registration_phone = ''
    st.session_state.registration_name = ''
    st.session_state.confirm_delete = {}

def get_session_summary() -> Dict[str, Any]:
    """Получить сводку состояния сессии (для отладки)"""
    return {
        'client': get_client_session(),
        'admin': get_admin_session(),
        'ui': get_ui_state(),
        'forms_visible': is_any_form_visible(),
        'auth_initialized': is_auth_table_initialized()
    }