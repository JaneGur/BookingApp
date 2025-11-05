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
    """Роутинг админ-панели"""
    
    # Инициализация страницы
    if 'admin_page' not in st.session_state:
        st.session_state.admin_page = "main"
    
    # Роутинг
    if st.session_state.admin_page == "client_profile":
        # Показываем страницу профиля
        from .client_profile import render_client_profile
        render_client_profile()
    else:
        # Показываем обычную панель с табами
        st.session_state.admin_page = "main"
        
        # Заголовок
        st.markdown("""
        <div style="background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%); 
             padding: 2rem 2.5rem; border-radius: 16px; margin-bottom: 2rem;
             box-shadow: 0 4px 20px rgba(136, 200, 188, 0.25);">
            <h1 style="color: white; font-size: 1.75rem; font-weight: 700; margin: 0; 
                 letter-spacing: -0.02em; display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 2rem;">👩‍💼</span>
                Панель управления
            </h1>
            <p style="color: rgba(255, 255, 255, 0.9); margin: 0.5rem 0 0 0; font-size: 1rem;">
                Система управления записями и клиентами
            </p>
        </div>
        """, unsafe_allow_html=True)
        
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
            # ВАЖНО: Используем новую компактную версию
            from .tabs.clients_tab_compact import render_clients_tab_compact
            render_clients_tab_compact(client_service, booking_service)
        
        with tabs[2]:
            render_products_tab()
        
        with tabs[3]:
            render_blocking_tab()
        
        with tabs[4]:
            render_analytics_tab(analytics_service)
        
        with tabs[5]:
            render_settings_tab(settings_service, notification_service)