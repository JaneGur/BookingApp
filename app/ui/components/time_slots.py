import streamlit as st
from typing import List, Optional
from services.booking_service import BookingService

def render_time_slots(available_slots: List[str], key_prefix: str = "slot") -> Optional[str]:
    """Отрисовка временных слотов"""
    if not available_slots:
        st.warning("😔 На выбранную дату нет свободных слотов")
        return None
    
    st.markdown("#### 🕐 Выберите время")
    st.info("💡 Доступные для записи временные слоты")
    
    # Инициализация selected_time в session_state если его нет
    if 'selected_time' not in st.session_state:
        st.session_state.selected_time = None
    
    cols = st.columns(4)
    for idx, time_slot in enumerate(available_slots):
        with cols[idx % 4]:
            # Определяем тип кнопки в зависимости от выбранного времени
            button_type = "primary" if st.session_state.selected_time != time_slot else "secondary"
            if st.button(
                f"🕐 {time_slot}", 
                key=f"{key_prefix}_{time_slot}", 
                width='stretch',
                type=button_type,
                use_container_width=True
            ):
                # Если нажали на уже выбранное время - сбрасываем выбор
                if st.session_state.selected_time == time_slot:
                    st.session_state.selected_time = None
                else:
                    st.session_state.selected_time = time_slot
    
    return st.session_state.selected_time