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
    st.markdown("""
    <h3 style="color: #225c52; font-size: 1.4rem; font-weight: 600; 
         margin-bottom: 1.25rem; padding-bottom: 0.75rem; 
         border-bottom: 2px solid rgba(136, 200, 188, 0.2);">
        👥 База клиентов
    </h3>
    """, unsafe_allow_html=True)
    
    # ===== ВЕРХНЯЯ ПАНЕЛЬ С ДЕЙСТВИЯМИ =====
    render_top_actions()
    
    # ===== ФОРМА НОВОЙ ЗАПИСИ (если активирована) =====
    if st.session_state.get('show_new_booking_form'):
        render_new_booking_form(client_service, booking_service)
        st.markdown("---")
    
    # ===== ПОИСК И ФИЛЬТРЫ =====
    search_query, show_only_active = render_search_and_filters()
    
    # ===== ЗАГРУЗКА ДАННЫХ =====
    clients_df = client_service.get_all_clients()
    
    if clients_df.empty:
        render_empty_state()
        return
    
    # ===== ПРИМЕНЕНИЕ ФИЛЬТРОВ =====
    clients_df = apply_filters(clients_df, search_query, show_only_active)
    
    # ===== СТАТИСТИКА =====
    render_summary_statistics(clients_df)
    
    # ===== СПИСОК КЛИЕНТОВ =====
    st.markdown("---")
    render_clients_list_enhanced(clients_df, client_service, booking_service)


# ========== КОМПОНЕНТЫ ИНТЕРФЕЙСА ==========

def render_top_actions():
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
    """Применение фильтров к данным"""
    # Фильтр поиска
    if search_query:
        mask = (
            clients_df['client_name'].str.contains(search_query, case=False, na=False) | 
            clients_df['client_phone'].str.contains(search_query, case=False, na=False)
        )
        clients_df = clients_df[mask]
    
    # Фильтр активности
    if show_only_active:
        clients_df = clients_df[clients_df['upcoming_bookings'] > 0]
    
    return clients_df


def render_summary_statistics(clients_df):
    """Сводная статистика"""
    if st.session_state.get('show_stats'):
        st.markdown("---")
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


def render_clients_list_enhanced(clients_df, client_service, booking_service):
    """Улучшенный список клиентов"""
    st.markdown(f"#### 👥 Список клиентов ({len(clients_df)})")
    
    if clients_df.empty:
        st.info("По вашему запросу клиенты не найдены")
        return
    
    # Сортировка: сначала активные, потом по имени
    clients_df = clients_df.sort_values(
        ['upcoming_bookings', 'client_name'], 
        ascending=[False, True]
    )
    
    for idx, client in clients_df.iterrows():
        render_client_card_compact(client, client_service, booking_service)


def render_client_card_compact(client, client_service, booking_service):
    """Компактная карточка клиента"""
    client_key = f"client_{client['phone_hash']}"
    
    # Определяем статус клиента
    is_active = client['upcoming_bookings'] > 0
    status_badge = "🟢 Активен" if is_active else "⚪️ Неактивен"
    status_color = "#10b981" if is_active else "#9ca3af"
    
    # Основная карточка
    with st.container():
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.95); padding: 1.25rem; border-radius: 12px; 
             border-left: 4px solid {status_color}; margin-bottom: 1rem;
             box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                <div>
                    <h4 style="margin: 0; color: #2d5a4f; font-size: 1.1rem;">
                        👤 {client['client_name']}
                    </h4>
                    <p style="margin: 0.25rem 0 0 0; color: #6b7280; font-size: 0.9rem;">
                        📱 {client['client_phone']}
                    </p>
                </div>
                <span style="background: rgba{('16, 185, 129' if is_active else '156, 163, 175')}, 0.1); 
                     color: {status_color}; padding: 0.25rem 0.75rem; border-radius: 12px; 
                     font-size: 0.85rem; font-weight: 600;">
                    {status_badge}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Детали и действия
        col_info, col_actions = st.columns([3, 1])
        
        with col_info:
            render_client_info_inline(client)
        
        with col_actions:
            render_client_actions_compact(client, client_key, client_service, booking_service)
        
        st.markdown("---")


def render_client_info_inline(client):
    """Информация о клиенте в строчном формате"""
    # Метрики в одну строку
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📅 Всего", client['total_bookings'], label_visibility="visible")
    
    with col2:
        st.metric("⏰ Предстоящих", client['upcoming_bookings'], label_visibility="visible")
    
    with col3:
        st.metric("✅ Завершено", client['completed_bookings'], label_visibility="visible")
    
    with col4:
        st.metric("❌ Отменено", client['cancelled_bookings'], label_visibility="visible")
    
    # Дополнительная информация (только если есть)
    details = []
    if client.get('client_email'):
        details.append(f"📧 {client['client_email']}")
    if client.get('client_telegram'):
        details.append(f"💬 {client['client_telegram']}")
    
    if details:
        st.caption(" · ".join(details))


def render_client_actions_compact(client, client_key, client_service, booking_service):
    """Компактные действия с клиентом"""
    # История записей
    history_label = "📋 Скрыть историю" if st.session_state.get('selected_client') == client['phone_hash'] else "📋 История"
    
    if st.button(history_label, key=f"history_{client_key}", use_container_width=True, type="primary"):
        if st.session_state.get('selected_client') == client['phone_hash']:
            st.session_state.selected_client = None
            st.session_state.selected_client_name = None
        else:
            st.session_state.selected_client = client['phone_hash']
            st.session_state.selected_client_name = client['client_name']
        st.rerun()
    
    # Удаление
    delete_key = f"delete_mode_{client_key}"
    
    if st.session_state.get(delete_key):
        render_delete_confirmation_inline(client, client_key, client_service, delete_key)
    else:
        if st.button("🗑️ Удалить", key=f"delete_{client_key}", use_container_width=True):
            st.session_state[delete_key] = True
            st.rerun()
    
    # История (если открыта)
    if st.session_state.get('selected_client') == client['phone_hash']:
        st.markdown("---")
        render_client_history_section(client, client_service, booking_service)


def render_delete_confirmation_inline(client, client_key, client_service, delete_key):
    """Подтверждение удаления"""
    st.warning("⚠️ Удалить клиента?")
    
    cascade = st.checkbox("С записями", key=f"cascade_{client_key}", value=False, help="Удалить клиента вместе со всеми его записями")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Да", key=f"confirm_del_{client_key}", use_container_width=True, type="primary"):
            ok, msg = client_service.delete_client_by_hash(client['phone_hash'], cascade_bookings=cascade)
            if ok:
                st.success(msg)
                st.session_state[delete_key] = False
                st.session_state.selected_client = None
                time_module.sleep(0.5)
                st.rerun()
            else:
                st.error(msg)
    
    with col2:
        if st.button("❌ Нет", key=f"cancel_del_{client_key}", use_container_width=True):
            st.session_state[delete_key] = False
            st.rerun()


def render_client_history_section(client, client_service, booking_service):
    """Секция истории записей"""
    st.markdown(f"#### 📋 История: {client['client_name']}")
    
    history_df = client_service.get_client_booking_history(client['phone_hash'])
    
    if not history_df.empty:
        # Фильтр по статусу для истории
        status_filter = st.multiselect(
            "Фильтр",
            options=['confirmed', 'pending_payment', 'completed', 'cancelled'],
            default=['confirmed', 'pending_payment', 'completed'],
            format_func=lambda x: {
                'confirmed': '✅ Подтверждена',
                'pending_payment': '🟡 Ожидает оплаты',
                'completed': '✅ Завершена',
                'cancelled': '❌ Отменена'
            }[x],
            key=f"history_filter_{client['phone_hash']}"
        )
        
        filtered_history = history_df[history_df['status'].isin(status_filter)]
        
        st.info(f"📊 Показано записей: {len(filtered_history)}")
        
        for _, booking in filtered_history.iterrows():
            render_client_booking_history(booking, booking_service)
    else:
        st.info("📭 История записей пуста")


def render_new_booking_form(client_service, booking_service):
    """Улучшенная форма создания заказа"""
    st.markdown("---")
    st.markdown("### ➕ Создание нового заказа")
    
    with st.expander("📝 Форма заказа", expanded=True):
        with st.form("new_booking_admin_form"):
            st.markdown("**👤 Клиент**")
            col_a, col_b = st.columns(2)
            
            with col_a:
                new_client_name = st.text_input(
                    "Имя *", 
                    placeholder="Иван Иванов", 
                    key="admin_new_client_name"
                )
                new_client_email = st.text_input(
                    "Email", 
                    placeholder="example@mail.com", 
                    key="admin_new_client_email"
                )
            
            with col_b:
                new_client_phone = st.text_input(
                    "Телефон *", 
                    placeholder="+7 (999) 123-45-67", 
                    key="admin_new_client_phone"
                )
                new_client_telegram = st.text_input(
                    "Telegram", 
                    placeholder="@username", 
                    key="admin_new_client_telegram"
                )
            
            st.markdown("---")
            st.markdown("**📅 Детали записи**")
            
            col_c, col_d = st.columns(2)
            
            with col_c:
                booking_date = st.date_input(
                    "Дата *", 
                    min_value=now_msk().date(), 
                    max_value=now_msk().date() + timedelta(days=30), 
                    key="admin_booking_date"
                )
            
            with col_d:
                booking_time = st.time_input(
                    "Время *", 
                    value=datetime.strptime("09:00", "%H:%M").time(), 
                    key="admin_booking_time"
                )
            
            booking_notes = st.text_area(
                "Комментарий", 
                height=80, 
                placeholder="Причина обращения или дополнительные пожелания...", 
                key="admin_booking_notes"
            )
            
            st.markdown("---")
            st.markdown("**💳 Продукт (опционально)**")
            
            # Получаем продукты
            prod_map = get_product_map()
            prod_items = sorted(
                [(pid, info.get('name'), info.get('price_rub')) for pid, info in prod_map.items()], 
                key=lambda x: (x[1] or "")
            )
            
            if prod_items:
                prod_labels = [f"{name} — {price} ₽" for _, name, price in prod_items]
                selected_prod_idx = st.selectbox(
                    "Выберите продукт", 
                    options=list(range(len(prod_items))), 
                    format_func=lambda i: prod_labels[i],
                    key="admin_select_product"
                )
            else:
                st.info("ℹ️ Продукты не настроены")
                selected_prod_idx = None
            
            st.markdown("---")
            
            col_submit, col_cancel = st.columns([1, 1])
            
            with col_submit:
                submit_booking = st.form_submit_button(
                    "✅ Создать заказ", 
                    use_container_width=True, 
                    type="primary"
                )
            
            with col_cancel:
                cancel_booking = st.form_submit_button(
                    "❌ Отмена", 
                    use_container_width=True
                )
            
            if cancel_booking:
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
                    
                    success, message = booking_service.create_booking(booking_data)
                    
                    if success:
                        # Сохраняем продукт
                        if selected_prod_idx is not None and prod_items:
                            try:
                                pid, name, price = prod_items[selected_prod_idx]
                                row = booking_service.get_booking_by_datetime(
                                    new_client_phone, 
                                    str(booking_date), 
                                    booking_time.strftime("%H:%M")
                                )
                                if row:
                                    booking_service.set_booking_payment_info(
                                        row['id'], 
                                        pid, 
                                        float(price or 0)
                                    )
                            except Exception:
                                pass
                        
                        st.success("✅ Заказ создан и ожидает оплаты")
                        st.session_state.show_new_booking_form = False
                        time_module.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)