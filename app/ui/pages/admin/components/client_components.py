import streamlit as st
import time as time_module
from datetime import datetime
from utils.formatters import format_date
from core.database import db_manager
from utils.datetime_helpers import now_msk

"""
Файл: app/ui/pages/admin/components/client_components.py
ОПТИМИЗИРОВАННАЯ версия - БЕЗ задержек
"""
import streamlit as st
from datetime import datetime
from utils.formatters import format_date
from utils.datetime_helpers import now_msk

@st.fragment
def render_client_booking_history(booking, booking_service):
    """ОПТИМИЗИРОВАННАЯ история - fragment для изоляции"""
    from config.constants import STATUS_DISPLAY
    
    status_info = STATUS_DISPLAY.get(booking['status'], STATUS_DISPLAY['confirmed'])
    booking_key = f"booking_{booking['id']}"
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            date_formatted = format_date(booking['booking_date'])
            st.write(f"**{status_info['emoji']} {date_formatted} {booking['booking_time']}** - {status_info['text']}")
            
            if booking['notes']:
                st.info(f"💭 {booking['notes']}")
            
            try:
                pid = booking.get('product_id')
                amount = booking.get('amount')
                if pid is not None or amount is not None:
                    from core.database import db_manager
                    supabase = db_manager.get_client()
                    pname = None
                    if pid is not None and supabase is not None:
                        resp = supabase.table('products').select('name').eq('id', pid).limit(1).execute()
                        if resp.data:
                            pname = resp.data[0].get('name')
                    pname_disp = pname or (f"ID {pid}" if pid is not None else '—')
                    st.write(f"🧾 Продукт: {pname_disp}{f', Сумма: {amount} ₽' if amount is not None else ''}")
            except Exception:
                pass
            
            if booking.get('created_at'):
                created_at_value = booking['created_at']
                created_at = format_date(created_at_value[:10]) if 'T' in created_at_value else format_date(created_at_value)
                st.caption(f"📅 Записано: {created_at}")
        
        with col2:
            edit_mode_key = f"edit_mode_{booking_key}"
            
            if st.session_state.get(edit_mode_key):
                st.markdown("**✏️ Редактирование**")
                if st.button("✖️ Закрыть", key=f"close_edit_{booking_key}", use_container_width=True):
                    st.session_state[edit_mode_key] = False
            else:
                st.markdown("**⚙️ Действия**")
                
                if st.button("✏️ Изменить", key=f"edit_{booking_key}", use_container_width=True):
                    st.session_state[edit_mode_key] = True
                
                if booking['status'] == 'pending_payment':
                    if st.button("💳 Оплачено", key=f"paid_{booking_key}", 
                               use_container_width=True, type="primary"):
                        success, message = booking_service.mark_booking_paid(booking['id'])
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
        
        # Форма редактирования
        if st.session_state.get(edit_mode_key):
            render_edit_form_fast(booking, booking_service, booking_key, edit_mode_key)
        
        st.markdown("---")


def render_edit_form_fast(booking, booking_service, booking_key, edit_mode_key):
    """Быстрая форма редактирования БЕЗ лишних обновлений"""
    
    with st.form(f"edit_form_{booking_key}"):
        st.markdown("##### Редактирование записи")
        
        col_e1, col_e2 = st.columns(2)
        
        with col_e1:
            cur_date = booking['booking_date']
            try:
                date_val = datetime.strptime(cur_date, "%Y-%m-%d").date()
            except:
                date_val = now_msk().date()
            
            new_date = st.date_input("Дата", value=date_val, key=f"date_{booking_key}")
        
        with col_e2:
            cur_time = booking['booking_time']
            try:
                time_val = datetime.strptime(cur_time, "%H:%M").time()
            except:
                time_val = datetime.strptime("09:00", "%H:%M").time()
            
            new_time = st.time_input("Время", value=time_val, key=f"time_{booking_key}")
        
        status_options = {
            'pending_payment': '🟡 Ожидает оплаты',
            'confirmed': '✅ Подтверждена',
            'cancelled': '❌ Отменена',
            'completed': '✅ Завершена'
        }
        new_status = st.selectbox(
            "Статус",
            options=list(status_options.keys()),
            format_func=lambda x: status_options[x],
            index=list(status_options.keys()).index(booking['status']),
            key=f"status_{booking_key}"
        )
        
        new_notes = st.text_area("Комментарий", value=booking['notes'] or '', 
                                height=80, key=f"notes_{booking_key}")
        
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            if st.form_submit_button("💾 Сохранить", use_container_width=True, type="primary"):
                # БЕЗ spinner - форма и так показывает процесс
                ok1, msg1 = booking_service.update_booking_details(
                    booking['id'],
                    new_date=str(new_date),
                    new_time=new_time.strftime("%H:%M") if new_time else None,
                    new_notes=new_notes
                )
                ok2, msg2 = booking_service.update_booking_status(booking['id'], new_status)
                
                if ok1 and ok2:
                    st.success("✅ Изменения сохранены")
                    st.session_state[edit_mode_key] = False
                else:
                    if not ok1:
                        st.error(msg1)
                    if not ok2:
                        st.error(msg2)
        
        with col_s2:
            if st.form_submit_button("❌ Отмена", use_container_width=True):
                st.session_state[edit_mode_key] = False