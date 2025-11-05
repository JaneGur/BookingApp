import streamlit as st
from services.settings_service import SettingsService
from services.notification_service import NotificationService
from ..settings import (
    render_schedule_settings,
    render_info_settings, 
    render_security_settings,
    render_notifications_settings,
    render_documents_settings
)

def render_settings_tab(settings_service, notification_service):
    
    """Вкладка настроек системы"""
  
    st.markdown("""
    <h3 style="color: #225c52; font-size: 1.4rem; font-weight: 600; 
         margin-bottom: 1.25rem; padding-bottom: 0.75rem; 
         border-bottom: 2px solid rgba(136, 200, 188, 0.2);">
        ⚙️ Настройки системы
    </h3>
    """, unsafe_allow_html=True)
    
    settings_tabs = st.tabs(["📅 Расписание", "ℹ️ Информационная панель", "🔐 Безопасность", "🔔 Уведомления", "📄 Документы"])
    
    with settings_tabs[0]:
        render_schedule_settings(settings_service)
    
    with settings_tabs[1]:
        render_info_settings(settings_service)

    with settings_tabs[2]:
        render_security_settings()

    with settings_tabs[3]:
        render_notifications_settings(notification_service)

    with settings_tabs[4]:
        render_documents_settings()