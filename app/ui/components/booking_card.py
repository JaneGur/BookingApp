import streamlit as st
from config.constants import STATUS_DISPLAY
from services.booking_service import BookingService
from services.notification_service import NotificationService
from utils.product_cache import get_product_map
from utils.first_session_cache import has_paid_first_consultation_cached

def render_booking_card(booking: dict, show_actions: bool = True):
    """Оптимизированная карточка - минимум реактивных элементов"""
    from config.constants import STATUS_DISPLAY
    
    status_info = STATUS_DISPLAY.get(booking['status'], STATUS_DISPLAY['confirmed'])
    
    # Используем container без лишних обновлений
    with st.container():
        col1, col2 = st.columns([4, 1]) if show_actions else st.columns([1])
        
        with col1:
            st.markdown(f"**{status_info['emoji']} {booking['booking_time']} - {booking['client_name']}**")
            st.text(f"📱 {booking['client_phone']}")
            
            if booking.get('notes'):
                st.text(f"💭 {booking['notes']}")
            
            # Продукт (без лишних запросов)
            if booking.get('product_id'):
                try:
                    from utils.product_cache import get_product_name
                    pname = get_product_name(booking['product_id'])
                    if pname:
                        st.text(f"🧾 {pname}")
                except:
                    pass
        
        if show_actions and col2:
            with col2:
                # ВАЖНО: используем popover для действий вместо прямых кнопок
                # Это предотвращает лишние rerun
                with st.popover("⚙️ Действия", use_container_width=True):
                    if booking.get('status') == 'pending_payment':
                        if st.button("💳 Оплачено", key=f"paid_{booking['id']}", width='stretch'):
                            process_payment_fast(booking['id'])
                    
                    if st.button("🗑️ Удалить", key=f"del_{booking['id']}", width='stretch'):
                        delete_booking_fast(booking['id'])
        
        st.markdown("---")


# ========== 5. БЫСТРЫЕ ОПЕРАЦИИ С МИНИМАЛЬНЫМИ ЗАПРОСАМИ ==========

def process_payment_fast(booking_id: int):
    """Быстрая отметка оплаты"""
    with st.spinner("💳 Обработка..."):
        from services.booking_service import BookingService
        bs = BookingService()
        
        success, msg = bs.mark_booking_paid(booking_id)
        
        if success:
            st.success(msg)
            time.sleep(0.3)
        else:
            st.error(msg)
            time.sleep(0.5)
        
        st.rerun()

def delete_booking_fast(booking_id: int):
    """Быстрое удаление"""
    with st.spinner("🗑️ Удаление..."):
        from services.booking_service import BookingService
        bs = BookingService()
        
        if bs.delete_booking(booking_id):
            st.success("✅ Удалено")
            time.sleep(0.2)
        else:
            st.error("❌ Ошибка")
            time.sleep(0.3)
        
        st.rerun()
