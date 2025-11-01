import streamlit as st
from services.booking_service import BookingService

@st.cache_data(ttl=300, show_spinner=False)
def has_paid_first_consultation_cached(phone: str) -> bool:
    """Кэшированная проверка: у клиента уже оплачена первая консультация?
    Кэш по номеру телефона на 5 минут.
    """
    try:
        bs = BookingService()
        return bs.has_paid_first_consultation(phone)
    except Exception:
        return False
