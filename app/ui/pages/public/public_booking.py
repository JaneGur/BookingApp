import streamlit as st
import time
from services.booking_service import BookingService
from services.client_service import ClientService
from ui.components import render_info_panel

from .components.progress_indicator import render_progress_indicator
from .components.step_datetime import render_step_datetime
from .components.step_user_data import render_step_user_data
from .components.step_confirmation import render_step_confirmation
from .components.step_authorization import render_step_authorization
from .utils.scroll_helpers import render_scroll_script

def render_public_booking():
    """Отрисовка публичной страницы записи с улучшенным балансом"""
    
    # Инициализация состояния шагов
    if 'booking_step' not in st.session_state:
        st.session_state.booking_step = 1
    if 'booking_form_data' not in st.session_state:
        st.session_state.booking_form_data = {}
    
    booking_service = BookingService()
    client_service = ClientService()
    
    # Более сбалансированное соотношение: 3:2 для лучшей читаемости
    col1, col2 = st.columns([3, 2], gap="large")
    
    with col1:
        render_booking_steps(booking_service, client_service)
    
    with col2:
        render_info_panel()

def render_booking_steps(booking_service, client_service):
    """Отрисовка пошаговой формы с мобильной навигацией"""
    current_step = st.session_state.booking_step
    
    # Индикатор прогресса
    render_progress_indicator(current_step)
    
    st.markdown("---")
    
    # Отрисовка текущего шага
    if current_step == 1:
        render_step_datetime(booking_service)
    elif current_step == 2:
        render_step_user_data()
    elif current_step == 3:
        render_step_confirmation(booking_service)
    elif current_step == 4:
        render_step_authorization(booking_service, client_service)
    
    # Скрипт для автоматической прокрутки
    render_scroll_script(current_step)