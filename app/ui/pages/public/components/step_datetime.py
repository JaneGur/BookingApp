import streamlit as st
import time
from datetime import timedelta
from config.constants import BOOKING_RULES
from utils.datetime_helpers import now_msk
from ..utils.scroll_helpers import render_step_anchor, render_field_anchor, render_navigation_anchor

def render_step_datetime(booking_service):
    """Шаг 1: Выбор даты и времени с якорями"""
    render_step_anchor("step1-form")
    st.markdown("### 📅 Шаг 1: Выберите дату и время")
    st.caption("Всё время — по Москве (MSK)")
    
    # Выбор даты
    min_date = now_msk().date()
    max_date = min_date + timedelta(days=BOOKING_RULES["MAX_DAYS_AHEAD"])
    
    render_field_anchor("date-picker")
    selected_date = st.date_input(
        "Дата консультации", 
        min_value=min_date,
        max_value=max_date, 
        value=st.session_state.booking_form_data.get('date', min_date),
        format="DD.MM.YYYY",
        key="step1_date"
    )
    
    # Получаем доступные слоты
    available_slots = booking_service.get_available_slots(str(selected_date))
    
    if not available_slots:
        st.warning("😔 На выбранную дату нет свободных слотов. Выберите другую дату.")
        return
    
    render_field_anchor("time-slots")
    st.markdown("#### 🕐 Доступные временные слоты")
    st.info(f"💡 Доступно {len(available_slots)} слотов на {selected_date.strftime('%d.%m.%Y')}")
    
    # Отображение слотов в сетке
    cols = st.columns(4)
    selected_time = st.session_state.booking_form_data.get('time')
    
    for idx, time_slot in enumerate(available_slots):
        with cols[idx % 4]:
            is_selected = (time_slot == selected_time)
            button_type = "primary" if is_selected else "secondary"
            label = f"{'✓ ' if is_selected else ''}🕐 {time_slot}"
            if st.button(label, key=f"slot_{time_slot}", use_container_width=True, type=button_type):
                with st.spinner("⏳ Загружаем выбранное время..."):
                    time.sleep(0.2)
                    st.session_state.booking_form_data['date'] = selected_date
                    st.session_state.booking_form_data['time'] = time_slot
                    st.rerun()
    
    # Кнопки навигации
    st.markdown("---")
    render_navigation_anchor(1)
    col_nav1, col_nav2 = st.columns([1, 1])
    
    with col_nav2:
        if selected_time:
            if st.button("Далее ➡️", use_container_width=True, type="primary", key="step1_next"):
                with st.spinner("🚪 Переходим на следующий шаг..."):
                    time.sleep(0.2)
                st.session_state.booking_step = 2
                st.rerun()
        else:
            st.button("Выберите время", use_container_width=True, disabled=True)