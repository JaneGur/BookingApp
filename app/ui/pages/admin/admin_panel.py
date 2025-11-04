import streamlit as st
from services.booking_service import BookingService
from services.client_service import ClientService
from services.analytics_service import AnalyticsService
from services.settings_service import SettingsService
from services.notification_service import NotificationService

from .tabs.bookings_tab import render_bookings_tab
from .tabs.clients_tab import render_clients_tab
from .tabs.products_tab import render_products_tab
from .tabs.blocking_tab import render_blocking_tab
from .tabs.analytics_tab import render_analytics_tab
from .tabs.settings_tab import render_settings_tab

def render_admin_panel():
    """Отрисовка панели администратора"""
    st.title("👩‍💼 Панель управления")
    
    # Инициализация сервисов
    booking_service = BookingService()
    client_service = ClientService()
    analytics_service = AnalyticsService()
    settings_service = SettingsService()
    notification_service = NotificationService()
    
    tabs = st.tabs(["📋 Записи", "👥 Клиенты", "💳 Продукты", "🚫 Блокировки", "📊 Аналитика", "⚙️ Настройки"])
    
    with tabs[0]:
        render_bookings_tab(booking_service)
    
    with tabs[1]:
        render_clients_tab(client_service, booking_service)
    
    with tabs[2]:
        render_products_tab()
    
    with tabs[3]:
        render_blocking_tab()
    
    with tabs[4]:
        render_analytics_tab(analytics_service)
    
    with tabs[5]:
        render_settings_tab(settings_service, notification_service)