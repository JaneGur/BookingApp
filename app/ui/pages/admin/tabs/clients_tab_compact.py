"""
Файл 1: app/ui/pages/admin/client_profile.py
Полноценная страница профиля клиента с историей и редактированием

Файл 2: app/ui/pages/admin/tabs/clients_tab.py (ОБНОВЛЕННАЯ ВЕРСИЯ)
Компактный список клиентов с переходом на профиль
"""

# ============== ФАЙЛ 2: ОБНОВЛЕННАЯ ВКЛАДКА КЛИЕНТОВ ==============

def render_clients_tab_compact(client_service, booking_service):
    """КОМПАКТНАЯ вкладка управления клиентами - список без развернутой истории"""
    st.markdown("""
    <h3 style="color: #225c52; font-size: 1.4rem; font-weight: 600; 
         margin-bottom: 1.25rem; padding-bottom: 0.75rem; 
         border-bottom: 2px solid rgba(136, 200, 188, 0.2);">
        👥 База клиентов
    </h3>
    """, unsafe_allow_html=True)
    
    # Верхняя панель
    render_top_actions_compact()
    
    # Форма новой записи (если активирована)
    if st.session_state.get('show_new_booking_form'):
        from .clients_tab import render_new_booking_form
        render_new_booking_form(client_service, booking_service)
        st.markdown("---")
    
    # Поиск и фильтры
    search_query, show_only_active = render_search_and_filters()
    
    # Загрузка данных
    clients_df = client_service.get_all_clients()
    
    if clients_df.empty:
        render_empty_state()
        return
    
    # Применение фильтров
    clients_df = apply_filters(clients_df, search_query, show_only_active)
    
    # Статистика
    if st.session_state.get('show_stats'):
        render_summary_statistics(clients_df)
        st.markdown("---")
    
    # КОМПАКТНЫЙ список клиентов
    st.markdown(f"#### 👥 Список клиентов ({len(clients_df)})")
    
    if clients_df.empty:
        st.info("По вашему запросу клиенты не найдены")
        return
    
    # Сортировка
    clients_df = clients_df.sort_values(['upcoming_bookings', 'client_name'], ascending=[False, True])
    
    for idx, client in clients_df.iterrows():
        render_client_card_super_compact(client)


def render_top_actions_compact():
    """Верхняя панель с действиями"""
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown("#### 📋 Быстрые действия")
    
    with col2:
        if st.button("🔄 Обновить", use_container_width=True, key="refresh_clients"):
            st.rerun()
    
    with col3:
        stats_label = "📊 Скрыть статистику" if st.session_state.get('show_stats') else "📊 Показать статистику"
        if st.button(stats_label, use_container_width=True, key="toggle_stats"):
            st.session_state.show_stats = not st.session_state.get('show_stats', False)
            st.rerun()
    
    with col4:
        if st.button("➕ Создать заказ", use_container_width=True, type="primary", key="new_booking_btn"):
            st.session_state.show_new_booking_form = not st.session_state.get('show_new_booking_form', False)
            st.rerun()


def render_client_card_super_compact(client):
    """СУПЕР-КОМПАКТНАЯ карточка клиента - только основная информация + кнопка профиля"""
    
    is_active = client['upcoming_bookings'] > 0
    status_badge = "🟢 Активен" if is_active else "⚪️ Неактивен"
    status_color = "#10b981" if is_active else "#9ca3af"
    
    with st.container():
        col_info, col_metrics, col_actions = st.columns([3, 2, 1])
        
        with col_info:
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.95); padding: 1rem; border-radius: 12px; 
                 border-left: 4px solid {status_color}; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);">
                <h4 style="margin: 0 0 0.5rem 0; color: #2d5a4f; font-size: 1.05rem;">
                    👤 {client['client_name']}
                </h4>
                <p style="margin: 0.25rem 0; color: #6b7280; font-size: 0.9rem;">
                    📱 {client['client_phone']}
                </p>
                <span style="background: rgba{('16, 185, 129' if is_active else '156, 163, 175')}, 0.1); 
                     color: {status_color}; padding: 0.2rem 0.6rem; border-radius: 12px; 
                     font-size: 0.8rem; font-weight: 600; display: inline-block; margin-top: 0.5rem;">
                    {status_badge}
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        with col_metrics:
            # Компактные метрики в 2x2
            met_col1, met_col2 = st.columns(2)
            with met_col1:
                st.metric("📅 Всего", client['total_bookings'], label_visibility="visible", help="Всего записей")
                st.metric("✅ Завершено", client['completed_bookings'], label_visibility="visible")
            with met_col2:
                st.metric("⏰ Предстоящих", client['upcoming_bookings'], label_visibility="visible")
                st.metric("❌ Отменено", client['cancelled_bookings'], label_visibility="visible")
        
        with col_actions:
            # Кнопка открытия профиля
            if st.button("👁️ Профиль", key=f"profile_{client['phone_hash']}", 
                        use_container_width=True, type="primary",
                        help="Открыть полный профиль клиента"):
                st.session_state.admin_page = "client_profile"
                st.session_state.selected_client = client['phone_hash']
                st.session_state.selected_client_name = client['client_name']
                st.rerun()
            
            # Быстрое удаление (с подтверждением)
            delete_key = f"delete_confirm_{client['phone_hash']}"
            if st.session_state.get(delete_key):
                if st.button("✅ Да, удалить", key=f"confirm_{client['phone_hash']}", 
                           use_container_width=True, type="secondary"):
                    from services.client_service import ClientService
                    cs = ClientService()
                    ok, msg = cs.delete_client_by_hash(client['phone_hash'], cascade_bookings=False)
                    if ok:
                        st.success(msg)
                        st.session_state[delete_key] = False
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(msg)
                
                if st.button("❌ Отмена", key=f"cancel_{client['phone_hash']}", use_container_width=True):
                    st.session_state[delete_key] = False
                    st.rerun()
            else:
                if st.button("🗑️", key=f"delete_{client['phone_hash']}", 
                           use_container_width=True, help="Удалить клиента"):
                    st.session_state[delete_key] = True
                    st.rerun()
        
        st.markdown("---")


# ============== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (из старого кода) ==============

def render_search_and_filters():
    """Поиск и фильтры"""
    st.markdown("---")
    st.markdown("#### 🔍 Поиск клиентов")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Поиск по имени или телефону", 
            placeholder="Введите имя или номер телефона...", 
            key="admin_client_search",
            label_visibility="collapsed"
        )
    
    with col2:
        show_only_active = st.checkbox(
            "Только активные", 
            value=False, 
            key="admin_active_filter",
            help="Клиенты с предстоящими записями"
        )
    
    return search_query, show_only_active


def render_empty_state():
    """Состояние без клиентов"""
    st.info("📭 В базе пока нет клиентов")
    st.markdown("""
    ### 🚀 Начните работу
    
    Создайте первый заказ для клиента, используя кнопку **"➕ Создать заказ"** выше.
    """)


def apply_filters(clients_df, search_query, show_only_active):
    """Применение фильтров"""
    if search_query:
        mask = (
            clients_df['client_name'].str.contains(search_query, case=False, na=False) | 
            clients_df['client_phone'].str.contains(search_query, case=False, na=False)
        )
        clients_df = clients_df[mask]
    
    if show_only_active:
        clients_df = clients_df[clients_df['upcoming_bookings'] > 0]
    
    return clients_df


def render_summary_statistics(clients_df):
    """Статистика"""
    st.markdown("#### 📊 Статистика")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Всего клиентов", len(clients_df))
    with col2:
        active = len(clients_df[clients_df['upcoming_bookings'] > 0])
        st.metric("✅ Активных", active)
    with col3:
        avg = clients_df['total_bookings'].mean() if len(clients_df) > 0 else 0
        st.metric("📊 Среднее записей", f"{avg:.1f}")
    with col4:
        total = clients_df['total_bookings'].sum()
        st.metric("📅 Всего записей", int(total))
import streamlit as st
import time
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
    
    # Проверяем, выбран ли клиент
    if not st.session_state.get('selected_client'):
        st.warning("⚠️ Клиент не выбран")
        if st.button("🔙 Вернуться к списку", use_container_width=True):
            st.session_state.admin_page = "clients"
            st.rerun()
        return
    
    client_service = ClientService()
    booking_service = BookingService()
    notification_service = NotificationService()
    
    # Получаем данные клиента
    phone_hash = st.session_state.selected_client
    history_df = client_service.get_client_booking_history(phone_hash)
    
    if history_df.empty:
        st.error("❌ Клиент не найден")
        if st.button("🔙 Вернуться к списку", use_container_width=True):
            st.session_state.admin_page = "clients"
            st.session_state.selected_client = None
            st.rerun()
        return
    
    # Берем данные из первой записи
    client_data = history_df.iloc[0]
    client_name = st.session_state.get('selected_client_name', client_data['client_name'])
    
    # Шапка профиля
    render_profile_header(client_name, client_data, history_df)
    
    st.markdown("---")
    
    # Вкладки профиля
    tabs = st.tabs(["📊 Обзор", "📋 История записей", "👤 Редактировать профиль", "🗑️ Удаление"])
    
    with tabs[0]:
        render_overview_tab(client_data, history_df, notification_service)
    
    with tabs[1]:
        render_history_tab(history_df, booking_service, notification_service)
    
    with tabs[2]:
        render_edit_tab(client_data, client_service, phone_hash)
    
    with tabs[3]:
        render_delete_tab(phone_hash, client_name, client_service)


def render_profile_header(client_name, client_data, history_df):
    """Шапка профиля клиента"""
    
    # Кнопка назад
    col_back, col_spacer = st.columns([1, 5])
    with col_back:
        if st.button("🔙 К списку", use_container_width=True):
            st.session_state.admin_page = "clients"
            st.session_state.selected_client = None
            st.session_state.selected_client_name = None
            st.rerun()
    
    # Заголовок с именем
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
    
    # Быстрая статистика
    col1, col2, col3, col4 = st.columns(4)
    
    total = len(history_df)
    upcoming = len(history_df[history_df['status'] == 'confirmed'])
    completed = len(history_df[history_df['status'] == 'completed'])
    cancelled = len(history_df[history_df['status'] == 'cancelled'])
    
    with col1:
        st.metric("📅 Всего записей", total)
    with col2:
        st.metric("⏰ Предстоящих", upcoming)
    with col3:
        st.metric("✅ Завершено", completed)
    with col4:
        st.metric("❌ Отменено", cancelled)


def render_overview_tab(client_data, history_df, notification_service):
    """Вкладка обзора"""
    st.markdown("### 📊 Общая информация")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👤 Контактные данные")
        st.text(f"📱 Телефон: {client_data['client_phone']}")
        if client_data.get('client_email'):
            st.text(f"📧 Email: {client_data['client_email']}")
        if client_data.get('client_telegram'):
            st.text(f"💬 Telegram: {client_data['client_telegram']}")
        
        # Статус уведомлений
        chat_id = notification_service.get_client_telegram_chat_id(client_data['client_phone'])
        if chat_id:
            st.success("🔔 Telegram-уведомления подключены")
        else:
            st.warning("🔕 Telegram-уведомления не подключены")
    
    with col2:
        st.markdown("#### 📊 Статистика")
        
        # Первая и последняя записи
        if not history_df.empty:
            first_booking = history_df['booking_date'].min()
            last_booking = history_df['booking_date'].max()
            st.text(f"📅 Первая запись: {format_date(first_booking)}")
            st.text(f"📅 Последняя запись: {format_date(last_booking)}")
            
            # Подсчитываем выручку (только для completed)
            completed_bookings = history_df[history_df['status'] == 'completed']
            if not completed_bookings.empty and 'amount' in completed_bookings.columns:
                total_revenue = completed_bookings['amount'].sum()
                if total_revenue > 0:
                    st.text(f"💰 Общая выручка: {total_revenue:,.0f} ₽")
    
    st.markdown("---")
    
    # Последние записи
    st.markdown("### 📋 Последние записи")
    recent = history_df.head(5)
    
    for _, booking in recent.iterrows():
        status_info = STATUS_DISPLAY.get(booking['status'], STATUS_DISPLAY['confirmed'])
        date_formatted = format_date(booking['booking_date'])
        
        st.markdown(f"""
        <div style="background: {status_info['bg_color']}; padding: 1rem; border-radius: 12px; 
             border-left: 4px solid {status_info['color']}; margin-bottom: 0.75rem;">
            <p style="font-size: 1.05rem; font-weight: 600; color: {status_info['color']}; margin: 0;">
                {status_info['emoji']} {date_formatted} в {booking['booking_time']} — {status_info['text']}
            </p>
            {f"<p style='margin: 0.5rem 0 0 0; color: #4a6a60;'>💭 {booking['notes']}</p>" if booking.get('notes') else ""}
        </div>
        """, unsafe_allow_html=True)


def render_history_tab(history_df, booking_service, notification_service):
    """Вкладка полной истории записей"""
    st.markdown("### 📋 Полная история записей")
    
    # Фильтры
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
    
    # Применяем фильтры
    filtered = history_df[history_df['status'].isin(status_filter)]
    
    if sort_order == 'desc':
        filtered = filtered.sort_values(['booking_date', 'booking_time'], ascending=False)
    else:
        filtered = filtered.sort_values(['booking_date', 'booking_time'], ascending=True)
    
    st.info(f"📊 Показано записей: {len(filtered)}")
    
    # Отображение записей
    st.markdown("---")
    
    if filtered.empty:
        st.info("Нет записей по выбранным фильтрам")
        return
    
    for _, booking in filtered.iterrows():
        render_booking_card_detailed(booking, booking_service, notification_service)


def render_booking_card_detailed(booking, booking_service, notification_service):
    """Детальная карточка записи с возможностью редактирования"""
    
    status_info = STATUS_DISPLAY.get(booking['status'], STATUS_DISPLAY['confirmed'])
    date_formatted = format_date(booking['booking_date'])
    
    booking_key = f"booking_{booking['id']}"
    edit_mode_key = f"edit_mode_{booking_key}"
    
    with st.container():
        if st.session_state.get(edit_mode_key):
            # Режим редактирования
            render_booking_edit_form(booking, booking_service, booking_key, edit_mode_key)
        else:
            # Обычный режим просмотра
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
                    {f"<p style='margin: 0.5rem 0; color: #4a6a60;'><strong>📅</strong> Создано: {format_date(booking['created_at'][:10])}</p>" if booking.get('created_at') else ""}
                </div>
                """, unsafe_allow_html=True)
            
            with col_actions:
                # Кнопка редактирования
                if st.button("✏️ Изменить", key=f"edit_{booking_key}", use_container_width=True, type="primary"):
                    st.session_state[edit_mode_key] = True
                    st.rerun()
                
                # Быстрая смена статуса
                if booking['status'] == 'pending_payment':
                    if st.button("💳 Оплачено", key=f"paid_{booking_key}", use_container_width=True):
                        with st.spinner("⏳ Обработка..."):
                            success, message = booking_service.mark_booking_paid(booking['id'])
                            if success:
                                st.success(message)
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(message)
        
        st.markdown("---")


def render_booking_edit_form(booking, booking_service, booking_key, edit_mode_key):
    """Форма редактирования записи"""
    
    with st.form(f"edit_form_{booking_key}"):
        st.markdown("##### ✏️ Редактирование записи")
        
        col_e1, col_e2 = st.columns(2)
        
        with col_e1:
            # Дата
            cur_date = booking['booking_date']
            try:
                date_val = datetime.strptime(cur_date, "%Y-%m-%d").date()
            except:
                date_val = now_msk().date()
            
            new_date = st.date_input("Дата", value=date_val, key=f"date_{booking_key}")
        
        with col_e2:
            # Время
            cur_time = booking['booking_time']
            try:
                time_val = datetime.strptime(cur_time, "%H:%M").time()
            except:
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
        new_notes = st.text_area("Комментарий", value=booking.get('notes', ''), height=100, key=f"notes_{booking_key}")
        
        # Кнопки
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            if st.form_submit_button("💾 Сохранить", use_container_width=True, type="primary"):
                with st.spinner("⏳ Сохранение..."):
                    # Обновляем детали
                    ok1, msg1 = booking_service.update_booking_details(
                        booking['id'],
                        new_date=str(new_date),
                        new_time=new_time.strftime("%H:%M"),
                        new_notes=new_notes
                    )
                    
                    # Обновляем статус
                    ok2, msg2 = booking_service.update_booking_status(booking['id'], new_status)
                    
                    if ok1 and ok2:
                        st.success("✅ Изменения сохранены")
                        st.session_state[edit_mode_key] = False
                        time.sleep(0.5)
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
                
                # Обновляем профиль
                if client_service.upsert_profile(
                    client_data['client_phone'],
                    new_name,
                    new_email,
                    new_telegram
                ):
                    st.success("✅ Профиль обновлен!")
                    st.session_state.selected_client_name = new_name
                    time.sleep(1)
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
            with st.spinner("Удаление..."):
                ok, msg = client_service.delete_client_by_hash(phone_hash, cascade_bookings=cascade)
                
                if ok:
                    st.success(msg)
                    st.session_state.admin_page = "clients"
                    st.session_state.selected_client = None
                    st.session_state.selected_client_name = None
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(msg)