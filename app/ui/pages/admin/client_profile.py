"""
Файл: app/ui/pages/admin/client_profile.py
РАСШИРЕННАЯ версия - с созданием заказов и редактированием записей
"""
import streamlit as st
from datetime import datetime
from services.client_service import ClientService
from services.booking_service import BookingService
from services.notification_service import NotificationService
from utils.formatters import format_date
from utils.validators import validate_email
from utils.datetime_helpers import now_msk
from config.constants import STATUS_DISPLAY

def render_client_profile():
    """Полноценная страница профиля клиента"""
    
    if not st.session_state.get('selected_client'):
        st.warning("⚠️ Клиент не выбран")
        if st.button("🔙 Вернуться к списку", use_container_width=True):
            st.session_state.admin_page = "clients"
            st.rerun()
        return
    
    client_service = ClientService()
    booking_service = BookingService()
    notification_service = NotificationService()
    
    phone_hash = st.session_state.selected_client
    history_df = client_service.get_client_booking_history(phone_hash)
    
    if history_df.empty:
        st.error("❌ Клиент не найден")
        if st.button("🔙 Вернуться к списку", use_container_width=True):
            st.session_state.admin_page = "clients"
            st.session_state.selected_client = None
            st.rerun()
        return
    
    client_data = history_df.iloc[0]
    client_name = st.session_state.get('selected_client_name', client_data['client_name'])
    
    render_profile_header(client_name, client_data, history_df)
    
    st.markdown("---")
    
    tabs = st.tabs(["📊 Обзор", "➕ Новая запись", "📋 История записей", "👤 Редактировать профиль", "🗑️ Удаление"])
    
    with tabs[0]:
        render_overview_tab(client_data, history_df, notification_service, booking_service)
    
    with tabs[1]:
        render_new_booking_tab(client_service, booking_service, client_data)
    
    with tabs[2]:
        render_history_tab(history_df, booking_service, notification_service)
    
    with tabs[3]:
        render_edit_tab(client_data, client_service, phone_hash)
    
    with tabs[4]:
        render_delete_tab(phone_hash, client_name, client_service)


def render_profile_header(client_name, client_data, history_df):
    """Шапка профиля клиента"""
    
    col_back, col_spacer = st.columns([1, 5])
    with col_back:
        if st.button("🔙 К списку", use_container_width=True):
            st.session_state.admin_page = "clients"
            st.session_state.selected_client = None
            st.session_state.selected_client_name = None
            st.rerun()
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%); 
         padding: 2rem 2.5rem; border-radius: 16px; margin: 1rem 0 2rem 0;
         box-shadow: 0 4px 20px rgba(136, 200, 188, 0.25);">
        <h1 style="color: white; font-size: 1.75rem; font-weight: 700; margin: 0; 
             letter-spacing: -0.02em; display: flex; align-items: center; gap: 0.75rem;">
            <span style="font-size: 2rem;">👤</span>
            {client_name}
        </h1>
        <p style="color: rgba(255, 255, 255, 0.9); margin: 0.5rem 0 0 0; font-size: 1rem;">
            📱 {client_data['client_phone']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    total = len(history_df)
    upcoming = len(history_df[history_df['status'] == 'confirmed'])
    completed = len(history_df[history_df['status'] == 'completed'])
    cancelled = len(history_df[history_df['status'] == 'cancelled'])
    
    with col1: st.metric("📅 Всего записей", total)
    with col2: st.metric("⏰ Предстоящих", upcoming)
    with col3: st.metric("✅ Завершено", completed)
    with col4: st.metric("❌ Отменено", cancelled)


def render_overview_tab(client_data, history_df, notification_service, booking_service):
    """Вкладка обзора с редактируемыми последними записями"""
    st.markdown("### 📊 Общая информация")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👤 Контактные данные")
        st.text(f"📱 Телефон: {client_data['client_phone']}")
        if client_data.get('client_email'):
            st.text(f"📧 Email: {client_data['client_email']}")
        if client_data.get('client_telegram'):
            st.text(f"💬 Telegram: {client_data['client_telegram']}")
        
        chat_id = notification_service.get_client_telegram_chat_id(client_data['client_phone'])
        if chat_id:
            st.success("🔔 Telegram-уведомления подключены")
        else:
            st.warning("🔕 Telegram-уведомления не подключены")
    
    with col2:
        st.markdown("#### 📊 Статистика")
        
        if not history_df.empty:
            first_booking = history_df['booking_date'].min()
            last_booking = history_df['booking_date'].max()
            st.text(f"📅 Первая запись: {format_date(first_booking)}")
            st.text(f"📅 Последняя запись: {format_date(last_booking)}")
            
            completed_bookings = history_df[history_df['status'] == 'completed']
            if not completed_bookings.empty and 'amount' in completed_bookings.columns:
                total_revenue = completed_bookings['amount'].sum()
                if total_revenue > 0:
                    st.text(f"💰 Общая выручка: {total_revenue:,.0f} ₽")
    
    st.markdown("---")
    
    # РЕДАКТИРУЕМЫЕ последние записи
    st.markdown("### 📋 Последние записи")
    recent = history_df.head(5)
    
    if not recent.empty:
        for _, booking in recent.iterrows():
            render_editable_booking_card(booking, booking_service, notification_service)
    else:
        st.info("📭 Нет записей")


def render_editable_booking_card(booking, booking_service, notification_service):
    """Редактируемая карточка записи"""
    
    status_info = STATUS_DISPLAY.get(booking['status'], STATUS_DISPLAY['confirmed'])
    date_formatted = format_date(booking['booking_date'])
    
    booking_key = f"overview_booking_{booking['id']}"
    edit_mode_key = f"edit_mode_{booking_key}"
    
    with st.container():
        if st.session_state.get(edit_mode_key):
            # Режим редактирования
            render_booking_edit_form_inline(booking, booking_service, booking_key, edit_mode_key)
        else:
            # Режим просмотра
            col_info, col_actions = st.columns([4, 1])
            
            with col_info:
                st.markdown(f"""
                <div style="background: {status_info['bg_color']}; padding: 1rem; border-radius: 12px; 
                     border-left: 4px solid {status_info['color']}; margin-bottom: 0.75rem;">
                    <p style="font-size: 1.05rem; font-weight: 600; color: {status_info['color']}; margin: 0;">
                        {status_info['emoji']} {date_formatted} в {booking['booking_time']} — {status_info['text']}
                    </p>
                    {f"<p style='margin: 0.5rem 0 0 0; color: #4a6a60;'>💭 {booking['notes']}</p>" if booking.get('notes') else ""}
                </div>
                """, unsafe_allow_html=True)
            
            with col_actions:
                if st.button("✏️", key=f"edit_{booking_key}", use_container_width=True, help="Редактировать"):
                    st.session_state[edit_mode_key] = True
                    st.rerun()
                
                if booking['status'] == 'pending_payment':
                    if st.button("💳", key=f"paid_{booking_key}", use_container_width=True, help="Оплачено"):
                        ok, msg = booking_service.mark_booking_paid(booking['id'])
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        
        st.markdown("---")


def render_booking_edit_form_inline(booking, booking_service, booking_key, edit_mode_key):
    """Инлайн-форма редактирования записи"""
    
    with st.form(f"edit_form_{booking_key}"):
        st.markdown("##### ✏️ Редактирование записи")
        
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
        
        new_notes = st.text_area("Комментарий", value=booking['notes'] or '', height=80, key=f"notes_{booking_key}")
        
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            if st.form_submit_button("💾 Сохранить", use_container_width=True, type="primary"):
                ok1, msg1 = booking_service.update_booking_details(
                    booking['id'],
                    new_date=str(new_date),
                    new_time=new_time.strftime("%H:%M"),
                    new_notes=new_notes
                )
                ok2, msg2 = booking_service.update_booking_status(booking['id'], new_status)
                
                if ok1 and ok2:
                    st.success("✅ Изменения сохранены")
                    st.session_state[edit_mode_key] = False
                    st.rerun()
                else:
                    if not ok1:
                        st.error(msg1)
                    if not ok2:
                        st.error(msg2)
        
        with col_s2:
            if st.form_submit_button("❌ Отмена", use_container_width=True):
                st.session_state[edit_mode_key] = False
                st.rerun()


def render_new_booking_tab(client_service, booking_service, client_data):
    """Вкладка создания новой записи"""
    st.markdown("### ➕ Создать новую запись")
    
    # Используем функцию из bookings_tab с префиксом "profile"
    from utils.product_cache import get_product_map
    from datetime import timedelta
    
    with st.form("new_booking_profile_form"):
        st.markdown("**📅 Детали записи**")
        
        col_c, col_d = st.columns(2)
        
        with col_c:
            booking_date = st.date_input("Дата *", min_value=now_msk().date(), 
                                       max_value=now_msk().date() + timedelta(days=30), key="booking_date_profile")
        
        with col_d:
            booking_time = st.time_input("Время *", value=datetime.strptime("09:00", "%H:%M").time(), key="booking_time_profile")
        
        booking_notes = st.text_area("Комментарий", height=80, placeholder="Причина обращения...", key="booking_notes_profile")
        
        st.markdown("---")
        st.markdown("**💳 Продукт**")
        
        prod_map = get_product_map()
        prod_items = sorted(
            [(pid, info.get('name'), info.get('price_rub')) for pid, info in prod_map.items()], 
            key=lambda x: (x[1] or "")
        )
        
        selected_prod_idx = None
        selected_prod_id = None
        selected_prod_price = None
        
        if prod_items:
            prod_labels = [f"{name} — {price} ₽" for _, name, price in prod_items]
            prod_labels.insert(0, "Без продукта")
            
            selected_idx = st.selectbox(
                "Выберите продукт", 
                options=list(range(len(prod_labels))), 
                format_func=lambda i: prod_labels[i],
                key="select_product_profile"
            )
            
            if selected_idx > 0:
                selected_prod_idx = selected_idx - 1
                selected_prod_id, _, selected_prod_price = prod_items[selected_prod_idx]
        else:
            st.info("ℹ️ Продукты не настроены")
        
        st.markdown("---")
        
        col_submit, col_cancel = st.columns([1, 1])
        
        with col_submit:
            submit_booking = st.form_submit_button("✅ Создать заказ", use_container_width=True, type="primary")
        
        with col_cancel:
            cancel_booking = st.form_submit_button("❌ Отмена", use_container_width=True)
        
        if cancel_booking:
            pass
        
        if submit_booking:
            booking_data = {
                'client_name': client_data['client_name'],
                'client_phone': client_data['client_phone'],
                'client_email': client_data.get('client_email', ''),
                'client_telegram': client_data.get('client_telegram', ''),
                'booking_date': str(booking_date),
                'booking_time': booking_time.strftime("%H:%M"),
                'notes': booking_notes,
                'status': 'pending_payment'
            }
            
            success, message = booking_service.create_booking(booking_data)
            
            if success:
                if selected_prod_id is not None:
                    try:
                        row = booking_service.get_booking_by_datetime(
                            client_data['client_phone'], 
                            str(booking_date), 
                            booking_time.strftime("%H:%M")
                        )
                        if row:
                            booking_service.set_booking_payment_info(
                                row['id'], 
                                selected_prod_id, 
                                float(selected_prod_price or 0)
                            )
                    except Exception as e:
                        st.warning(f"⚠️ Заказ создан, но не удалось привязать продукт: {e}")
                
                st.success("✅ Заказ создан и ожидает оплаты")
                st.rerun()
            else:
                st.error(message)


def render_history_tab(history_df, booking_service, notification_service):
    """Вкладка полной истории записей"""
    st.markdown("### 📋 Полная история записей")
    
    col_f1, col_f2 = st.columns([3, 1])
    
    with col_f1:
        status_filter = st.multiselect(
            "Фильтр по статусу",
            options=['confirmed', 'pending_payment', 'completed', 'cancelled'],
            default=['confirmed', 'pending_payment', 'completed'],
            format_func=lambda x: STATUS_DISPLAY[x]['text'],
            key="profile_status_filter"
        )
    
    with col_f2:
        sort_order = st.selectbox(
            "Сортировка",
            options=['desc', 'asc'],
            format_func=lambda x: "Сначала новые" if x == 'desc' else "Сначала старые",
            key="profile_sort"
        )
    
    filtered = history_df[history_df['status'].isin(status_filter)]
    
    if sort_order == 'desc':
        filtered = filtered.sort_values(['booking_date', 'booking_time'], ascending=False)
    else:
        filtered = filtered.sort_values(['booking_date', 'booking_time'], ascending=True)
    
    st.info(f"📊 Показано записей: {len(filtered)}")
    
    st.markdown("---")
    
    if filtered.empty:
        st.info("Нет записей по выбранным фильтрам")
        return
    
    for _, booking in filtered.iterrows():
        render_booking_card_detailed(booking, booking_service, notification_service)


def render_booking_card_detailed(booking, booking_service, notification_service):
    """Детальная карточка записи с редактированием"""
    
    status_info = STATUS_DISPLAY.get(booking['status'], STATUS_DISPLAY['confirmed'])
    date_formatted = format_date(booking['booking_date'])
    
    booking_key = f"booking_{booking['id']}"
    edit_mode_key = f"edit_mode_{booking_key}"
    
    with st.container():
        if st.session_state.get(edit_mode_key):
            render_booking_edit_form(booking, booking_service, booking_key, edit_mode_key)
        else:
            col_info, col_actions = st.columns([4, 1])
            
            with col_info:
                st.markdown(f"""
                <div style="background: {status_info['bg_color']}; padding: 1.25rem; border-radius: 12px; 
                     border-left: 4px solid {status_info['color']}; margin-bottom: 1rem;">
                    <p style="font-size: 1.15rem; font-weight: 600; color: {status_info['color']}; margin: 0 0 0.5rem 0;">
                        {status_info['emoji']} {date_formatted} в {booking['booking_time']}
                    </p>
                    <p style="margin: 0.5rem 0; color: #4a6a60;">
                        <strong>Статус:</strong> {status_info['text']}
                    </p>
                    {f"<p style='margin: 0.5rem 0; color: #4a6a60;'><strong>💭</strong> {booking['notes']}</p>" if booking.get('notes') else ""}
                </div>
                """, unsafe_allow_html=True)
            
            with col_actions:
                if st.button("✏️ Изменить", key=f"edit_{booking_key}", use_container_width=True, type="primary"):
                    st.session_state[edit_mode_key] = True
                    st.rerun()
                
                if booking['status'] == 'pending_payment':
                    if st.button("💳 Оплачено", key=f"paid_{booking_key}", use_container_width=True):
                        ok, msg = booking_service.mark_booking_paid(booking['id'])
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        
        st.markdown("---")


def render_booking_edit_form(booking, booking_service, booking_key, edit_mode_key):
    """Полная форма редактирования записи"""
    
    with st.form(f"edit_form_{booking_key}"):
        st.markdown("##### ✏️ Редактирование записи")
        
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
        
        new_notes = st.text_area("Комментарий", value=booking.get('notes', ''), height=100, key=f"notes_{booking_key}")
        
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            if st.form_submit_button("💾 Сохранить", use_container_width=True, type="primary"):
                ok1, msg1 = booking_service.update_booking_details(
                    booking['id'],
                    new_date=str(new_date),
                    new_time=new_time.strftime("%H:%M"),
                    new_notes=new_notes
                )
                ok2, msg2 = booking_service.update_booking_status(booking['id'], new_status)
                
                if ok1 and ok2:
                    st.success("✅ Изменения сохранены")
                    st.session_state[edit_mode_key] = False
                    st.rerun()
                else:
                    if not ok1:
                        st.error(msg1)
                    if not ok2:
                        st.error(msg2)
        
        with col_s2:
            if st.form_submit_button("❌ Отмена", use_container_width=True):
                st.session_state[edit_mode_key] = False
                st.rerun()


def render_edit_tab(client_data, client_service, phone_hash):
    """Вкладка редактирования профиля"""
    st.markdown("### 👤 Редактирование профиля клиента")
    
    with st.form("edit_client_profile"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("👤 Имя *", value=client_data['client_name'])
            new_email = st.text_input("📧 Email", value=client_data.get('client_email', ''))
        
        with col2:
            st.text_input("📱 Телефон", value=client_data['client_phone'], disabled=True, help="Телефон изменить нельзя")
            new_telegram = st.text_input("💬 Telegram", value=client_data.get('client_telegram', ''))
        
        col_save, col_cancel = st.columns([1, 1])
        
        with col_save:
            save = st.form_submit_button("💾 Сохранить изменения", use_container_width=True, type="primary")
        
        with col_cancel:
            cancel = st.form_submit_button("❌ Отмена", use_container_width=True)
        
        if save:
            if not new_name:
                st.error("❌ Имя обязательно для заполнения")
            else:
                if new_email:
                    email_valid, email_msg = validate_email(new_email)
                    if not email_valid:
                        st.error(email_msg)
                        return
                
                if client_service.upsert_profile(
                    client_data['client_phone'],
                    new_name,
                    new_email,
                    new_telegram
                ):
                    st.success("✅ Профиль обновлен!")
                    st.session_state.selected_client_name = new_name
                    st.rerun()
                else:
                    st.error("❌ Ошибка обновления профиля")


def render_delete_tab(phone_hash, client_name, client_service):
    """Вкладка удаления клиента"""
    st.markdown("### 🗑️ Удаление клиента")
    
    st.warning(f"""
    ⚠️ **Внимание!** Вы собираетесь удалить клиента **{client_name}**.
    
    Это действие необратимо.
    """)
    
    cascade = st.checkbox(
        "Удалить вместе со всеми записями",
        value=False,
        help="Если отмечено, удалятся также все записи клиента"
    )
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🗑️ Удалить клиента", use_container_width=True, type="primary"):
            ok, msg = client_service.delete_client_by_hash(phone_hash, cascade_bookings=cascade)
            
            if ok:
                st.success(msg)
                st.session_state.admin_page = "clients"
                st.session_state.selected_client = None
                st.session_state.selected_client_name = None
                st.rerun()
            else:
                st.error(msg)