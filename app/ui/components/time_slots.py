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
    
    cols = st.columns(4)
    for idx, time_slot in enumerate(available_slots):
        with cols[idx % 4]:
            if st.button(f"🕐 {time_slot}", key=f"{key_prefix}_{time_slot}", 
                        width='stretch', type="primary"):
                st.session_state.selected_time = time_slot
                st.rerun()
    
    return st.session_state.get('selected_time')