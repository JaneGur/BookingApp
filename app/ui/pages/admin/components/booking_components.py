import streamlit as st
from utils.formatters import format_date
from utils.datetime_helpers import now_msk, combine_msk
from datetime import timedelta
from services.notification_service import NotificationService
from utils.product_cache import get_product_map

def render_order_details(b, booking_service, prod_map):
    """Отрисовка деталей заказа"""
    colp1, colp2, colp3 = st.columns([2,1,1])
    
    with colp1:
        st.write(f"Телефон: {b.get('client_phone','')}")
        if b.get('notes'):
            st.info(f"💭 {b.get('notes')}")
        if b.get('product_id') is not None or b.get('amount') is not None:
            pid = b.get('product_id')
            if pid is not None and pid in prod_map:
                pname = prod_map[pid].get('name') or f"ID {pid}"
            else:
                pname = f"ID {pid}" if pid is not None else '—'
            amount = b.get('amount')
            st.write(f"Продукт: {pname}{(f', Сумма: {amount} ₽' if amount is not None else '')}")
        if b.get('status') in ('confirmed','completed'):
            try:
                consult_dt = combine_msk(b.get('booking_date',''), b.get('booking_time',''))
                reminder_dt = consult_dt - timedelta(hours=1)
                ns = NotificationService()
                chat_id = ns.get_client_telegram_chat_id(b.get('client_phone',''))
                client_state = "подключен" if chat_id else "не подключен"
                st.caption(f"⏰ Напоминание планируется на {reminder_dt.strftime('%d.%m.%Y %H:%M')} · Telegram клиента: {client_state}")
            except Exception:
                pass
    
    with colp2:
        status_val = b.get('status')
        if status_val == 'pending_payment':
            if st.button("💳 Пометить как оплачено", key=f"pending_paid_{b['id']}", use_container_width=True):
                ok, msg = booking_service.mark_booking_paid(b['id'])
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    
    with colp3:
        if st.button("❌ Отменить заказ", key=f"pending_cancel_{b['id']}", use_container_width=True):
            ok, msg = booking_service.update_booking_status(b['id'], 'cancelled')
            if ok:
                st.success("✅ Отменено")
                st.rerun()
            else:
                st.error(msg)