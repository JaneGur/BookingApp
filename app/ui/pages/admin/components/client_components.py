import streamlit as st
import time as time_module
from datetime import datetime
from utils.formatters import format_date
from core.database import db_manager
from utils.datetime_helpers import now_msk

def render_client_booking_history(booking, booking_service):
    """Отрисовка истории записей клиента"""
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
            # Управление записью
            edit_mode_key = f"edit_mode_{booking_key}"
            
            if st.session_state.get(edit_mode_key):
                # Режим редактирования
                st.markdown("**✏️ Редактирование**")
                
                # Закрыть редактирование
                if st.button("✖️ Закрыть", key=f"close_edit_{booking_key}", use_container_width=True):
                   with st.spinner("⏳ Закрываем..."):
                    time_module.sleep(0.2)
                    st.session_state[edit_mode_key] = False
                    st.rerun()
            else:
                # Обычный режим - показываем кнопки действий
                st.markdown("**⚙️ Действия**")
                
                # Кнопка редактирования
                if st.button("✏️ Изменить", key=f"edit_{booking_key}", use_container_width=True):
                    with st.spinner("⏳ Обработка..."):
                     time_module.sleep(0.2)
                    st.session_state[edit_mode_key] = True
                    st.rerun()
                
                # Быстрая смена статуса
                if booking['status'] == 'pending_payment':
                    if st.button("💳 Оплачено", key=f"paid_{booking_key}", use_container_width=True, type="primary"):
                        with st.spinner("⏳ Обработка..."):
                         time_module.sleep(0.2)
                        success, message = booking_service.mark_booking_paid(booking['id'])
                        if success:
                            st.success(message)
                            import time
                            time_module.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(message)
        
        # Форма редактирования (если включен режим редактирования)
        if st.session_state.get(edit_mode_key):
            st.markdown("---")
            with st.form(f"edit_form_{booking_key}"):
                st.markdown("##### Редактирование записи")
                
                col_e1, col_e2 = st.columns(2)
                
                with col_e1:
                    cur_date = booking['booking_date']
                    try:
                        date_val = datetime.strptime(cur_date, "%Y-%m-%d").date()
                    except Exception:
                        try:
                            date_val = datetime.strptime(cur_date[:10], "%Y-%m-%d").date()
                        except Exception:
                            date_val = now_msk().date()
                    
                    new_date = st.date_input("Дата", value=date_val, key=f"date_{booking_key}")
                
                with col_e2:
                    cur_time = booking['booking_time']
                    try:
                        time_val = datetime.strptime(cur_time, "%H:%M").time() if cur_time else datetime.strptime("09:00", "%H:%M").time()
                    except Exception:
                        time_val = datetime.strptime("09:00", "%H:%M").time()
                    
                    new_time = st.time_input("Время", value=time_val, key=f"time_{booking_key}")
                
                # Статус
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
                
                # Комментарий
                new_notes = st.text_area("Комментарий", value=booking['notes'] or '', height=80, key=f"notes_{booking_key}")
                
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    if st.form_submit_button("💾 Сохранить", use_container_width=True, type="primary"):
                        # Сохраняем изменения
                        with st.spinner("⏳ Обработка..."):
                         time_module.sleep(0.2)
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
                            import time
                            time_module.sleep(0.5)
                            st.rerun()
                        else:
                            if not ok1:
                                st.error(msg1)
                            if not ok2:
                                st.error(msg2)
                
                with col_s2:
                    if st.form_submit_button("❌ Отмена", use_container_width=True):
                        with st.spinner("⏳ Обработка..."):
                         time_module.sleep(0.2)
                        st.session_state[edit_mode_key] = False
                        st.rerun()
        
        st.markdown("---")