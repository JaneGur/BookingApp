import streamlit as st
import time as time_module
from datetime import datetime, timedelta
from services.client_service import ClientService
from services.booking_service import BookingService
from utils.datetime_helpers import now_msk
from utils.formatters import format_date
from utils.product_cache import get_product_map
from core.database import db_manager
from ..components.client_components import render_client_booking_history
from ..components.ui_components import render_client_stats

def render_clients_tab(client_service, booking_service):
    """Вкладка управления клиентами"""
    st.markdown("### 👥 База клиентов")
    
    # Поиск и фильтры
    st.markdown("#### 🔍 Поиск и фильтры")
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Поиск по имени или телефону", 
                                   placeholder="Введите имя или телефон...", 
                                   key="admin_client_search")
    with col2:
        show_only_active = st.checkbox("Только с предстоящими записями", 
                                     value=False, key="admin_active_filter")
    
    # Кнопки действий
    render_action_buttons()
    
    # Форма создания новой записи
    if st.session_state.get('show_new_booking_form'):
        render_new_booking_form(client_service, booking_service)
    
    # Получаем данные о клиентах
    clients_df = client_service.get_all_clients()
    
    if not clients_df.empty:
        # Применяем фильтры
        if search_query:
            mask = (clients_df['client_name'].str.contains(search_query, case=False, na=False)) | \
                   (clients_df['client_phone'].str.contains(search_query, case=False, na=False))
            clients_df = clients_df[mask]
        
        if show_only_active:
            clients_df = clients_df[clients_df['upcoming_bookings'] > 0]
        
        st.info(f"📊 Найдено клиентов: {len(clients_df)}")
        
        # Быстрая статистика
        render_client_stats(clients_df)
        
        # Отображаем клиентов
        render_clients_list(clients_df, client_service, booking_service)
        
        # Сводная статистика
        render_summary_stats(clients_df)
    else:
        st.info("📭 В базе нет клиентов")

def render_action_buttons():
    """Кнопки действий"""
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn1:
        if st.button("🔄 Обновить список", use_container_width=True, key="refresh_clients"):
            with st.spinner("⏳ Обработка..."):
                time_module.sleep(0.2)
            st.rerun()
    with col_btn2:
        if st.button("📊 Статистика", use_container_width=True, key="toggle_stats"):
            with st.spinner("⏳ Обработка..."):
                time_module.sleep(0.2)
            st.session_state.show_stats = not st.session_state.get('show_stats', False)
    with col_btn3:
        if st.button("➕ Новая запись", use_container_width=True, type="primary", key="new_booking_btn"):
            with st.spinner("⏳ Обработка..."):
                time_module.sleep(0.2)
            st.session_state.show_new_booking_form = True

def render_new_booking_form(client_service, booking_service):
    """Форма создания новой записи"""
    st.markdown("---")
    st.markdown("#### 📝 Создание нового заказа (ожидает оплаты)")
    
    with st.form("new_booking_admin_form"):
        st.markdown("**Информация о клиенте:**")
        col_a, col_b = st.columns(2)
        with col_a:
            new_client_name = st.text_input("👤 Имя клиента *", placeholder="Иван Иванов", key="admin_new_client_name")
            new_client_email = st.text_input("📧 Email", placeholder="example@mail.com", key="admin_new_client_email")
        with col_b:
            new_client_phone = st.text_input("📱 Телефон *", placeholder="+7 (999) 123-45-67", key="admin_new_client_phone")
            new_client_telegram = st.text_input("💬 Telegram", placeholder="@username", key="admin_new_client_telegram")
        
        st.markdown("**Детали записи:**")
        col_c, col_d = st.columns(2)
        with col_c:
            booking_date = st.date_input("📅 Дата записи", min_value=now_msk().date(), 
                                       max_value=now_msk().date() + timedelta(days=30), key="admin_booking_date")
        with col_d:
            booking_time = st.time_input("🕐 Время записи", value=datetime.strptime("09:00", "%H:%M").time(), key="admin_booking_time")
        
        booking_notes = st.text_area("💭 Причина встречи / комментарий", height=100, 
                                   placeholder="Опишите причину обращения или дополнительные пожелания...", 
                                   key="admin_booking_notes")

        st.markdown("**Продукт и оплата:**")
        prod_map = get_product_map()
        prod_items = sorted([(pid, info.get('name'), info.get('price_rub')) for pid, info in prod_map.items()], key=lambda x: (x[1] or ""))
        prod_labels = [f"{name} — {price} ₽" for _, name, price in prod_items]
        
        # Плашка с продуктом по умолчанию
        try:
            supabase = db_manager.get_client()
            rows = supabase.table('products').select('id,name,price_rub,is_featured,is_active').eq('is_active', True).order('sort_order').execute().data or []
            featured = [p for p in rows if p.get('is_featured')]
            chosen = (featured[0] if featured else (rows[0] if rows else None))
            if chosen:
                st.info(f"💳 По умолчанию будет оформлен: {chosen.get('name')} — {chosen.get('price_rub')} ₽ (можно изменить ниже)")
        except Exception:
            pass
        
        selected_prod_idx = st.selectbox("Выберите продукт (необязательно)", options=list(range(len(prod_items))) if prod_items else [], format_func=(lambda i: prod_labels[i] if prod_items else ""), index=0 if prod_items else None, key="admin_select_product") if prod_items else None
        
        col_submit, col_cancel = st.columns([1, 1])
        with col_submit:
            submit_booking = st.form_submit_button("✅ Создать заказ", use_container_width=True)
        with col_cancel:
            if st.form_submit_button("❌ Отмена", use_container_width=True):
                with st.spinner("⏳ Отменяем..."):
                    time_module.sleep(0.2)
                st.session_state.show_new_booking_form = False
                st.rerun()
        
        if submit_booking:
            if not new_client_name or not new_client_phone:
                st.error("❌ Заполните имя и телефон клиента")
            else:
                booking_data = {
                    'client_name': new_client_name,
                    'client_phone': new_client_phone,
                    'client_email': new_client_email,
                    'client_telegram': new_client_telegram,
                    'booking_date': str(booking_date),
                    'booking_time': booking_time.strftime("%H:%M"),
                    'notes': booking_notes,
                    'status': 'pending_payment'
                }
                # Создаём заказ (pending_payment)
                success, message = booking_service.create_booking(booking_data)
                if success:
                    # Сохраним выбранный продукт, если указан
                    try:
                        if selected_prod_idx is not None and prod_items:
                            pid, name, price = prod_items[selected_prod_idx]
                            # Получим созданную запись по дате/времени/телефону
                            row = booking_service.get_booking_by_datetime(new_client_phone, str(booking_date), booking_time.strftime("%H:%M"))
                            if row:
                                booking_service.set_booking_payment_info(row['id'], pid, float(price or 0))
                    except Exception:
                        pass
                    st.success("✅ Заказ создан и ожидает оплаты")
                    st.session_state.show_new_booking_form = False
                    st.rerun()
                else:
                    st.error(message)

def render_clients_list(clients_df, client_service, booking_service):
    """Отображение списка клиентов"""
    for idx, client in clients_df.iterrows():
        client_key = f"client_{client['phone_hash']}"
        
        with st.expander(f"👤 {client['client_name']} - 📱 {client['client_phone']} | 📅 Записей: {client['total_bookings']}", expanded=False):
            # Основная информация
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("**📇 Контактная информация:**")
                st.write(f"📧 Email: {client['client_email'] or 'Не указан'}")
                st.write(f"💬 Telegram: {client['client_telegram'] or 'Не указан'}")
                
                st.markdown("---")
                st.markdown("**📊 Статистика:**")
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                with col_stat1:
                    st.metric("Всего", client['total_bookings'])
                with col_stat2:
                    st.metric("Предстоящие", client['upcoming_bookings'])
                with col_stat3:
                    st.metric("Завершено", client['completed_bookings'])
                with col_stat4:
                    st.metric("Отменено", client['cancelled_bookings'])
                
                if client['first_booking'] or client['last_booking']:
                    st.markdown("---")
                    st.markdown("**📅 Даты:**")
                    if client['first_booking']:
                        st.caption(f"Первая запись: {format_date(client['first_booking'])}")
                    if client['last_booking']:
                        st.caption(f"Последняя запись: {format_date(client['last_booking'])}")
            
            with col2:
                render_client_actions(client, client_key, client_service)
            
            # История записей (если выбран этот клиент)
            if st.session_state.get('selected_client') == client['phone_hash']:
                render_client_booking_history_section(client, client_service, booking_service, client_key)

def render_client_actions(client, client_key, client_service):
    """Действия с клиентом"""
    st.markdown("**⚙️ Действия:**")
    
    # Кнопка истории записей
    if st.button("📋 История записей", key=f"show_history_{client_key}", use_container_width=True, type="primary"):
        with st.spinner("⏳ Обработка..."):
            time_module.sleep(0.2)
            if st.session_state.get('selected_client') == client['phone_hash']:
                # Если уже открыто - закрываем
                st.session_state.selected_client = None
                st.session_state.selected_client_name = None
            else:
                # Открываем историю
                st.session_state.selected_client = client['phone_hash']
                st.session_state.selected_client_name = client['client_name']
            st.rerun()
    
    # Кнопка удаления клиента
    delete_key = f"delete_mode_{client_key}"
    if st.session_state.get(delete_key):
        render_delete_confirmation(client, client_key, client_service, delete_key)
    else:
        if st.button("🗑️ Удалить клиента", key=f"delete_{client_key}", use_container_width=True):
            with st.spinner("⏳ Удаляем..."):
                time_module.sleep(0.2)
            st.session_state[delete_key] = True
            st.rerun()

def render_delete_confirmation(client, client_key, client_service, delete_key):
    """Подтверждение удаления клиента"""
    st.warning("⚠️ Удалить?")
    
    cascade = st.checkbox("С записями", key=f"cascade_{client_key}", value=False)
    
    col_del1, col_del2 = st.columns(2)
    with col_del1:
        if st.button("✅ Да", key=f"confirm_del_{client_key}", use_container_width=True):
            with st.spinner("⏳ Обработка..."):
                time_module.sleep(0.2)
                ok, msg = client_service.delete_client_by_hash(client['phone_hash'], cascade_bookings=cascade)
                if ok:
                    st.success(msg)
                    st.session_state[delete_key] = False
                    st.session_state.selected_client = None
                    time_module.sleep(0.5)
                    st.rerun()
                else:
                    st.error(msg)
    with col_del2:
        if st.button("❌ Нет", key=f"cancel_del_{client_key}", use_container_width=True):
            with st.spinner("⏳ Обработка..."):
                time_module.sleep(0.2)
            st.session_state[delete_key] = False
            st.rerun()

def render_client_booking_history_section(client, client_service, booking_service, client_key):
    """Секция истории записей клиента"""
    st.markdown("---")
    st.markdown(f"#### 📋 История записей: {client['client_name']}")
    
    # Кнопка закрытия истории
    if st.button("✖️ Скрыть историю", key=f"hide_history_{client_key}"):
        with st.spinner("⏳ Обработка..."):
            time_module.sleep(0.2)
        st.session_state.selected_client = None
        st.session_state.selected_client_name = None
        st.rerun()
    
    history_df = client_service.get_client_booking_history(client['phone_hash'])
    if not history_df.empty:
        for _, booking in history_df.iterrows():
            render_client_booking_history(booking, booking_service)
    else:
        st.info("📭 История записей пуста")

def render_summary_stats(clients_df):
    """Сводная статистика по клиентам"""
    st.markdown("---")
    st.markdown("### 📊 Сводная статистика по клиентам")
    
    col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
    with col_sum1:
        st.metric("Всего клиентов", len(clients_df))
    with col_sum2:
        active_clients = len(clients_df[clients_df['upcoming_bookings'] > 0])
        st.metric("Активных клиентов", active_clients)
    with col_sum3:
        avg_bookings = clients_df['total_bookings'].mean()
        st.metric("Среднее число записей", f"{avg_bookings:.1f}")
    with col_sum4:
        total_bookings = clients_df['total_bookings'].sum()
        st.metric("Всего записей", total_bookings)