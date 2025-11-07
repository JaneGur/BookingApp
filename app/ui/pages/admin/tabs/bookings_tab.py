"""
Файл: app/ui/pages/admin/tabs/bookings_tab.py
РАСШИРЕННАЯ версия - с созданием заказов и выбором продуктов
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from services.booking_service import BookingService
from utils.datetime_helpers import now_msk
from utils.formatters import format_date
from utils.product_cache import get_product_map
from config.constants import STATUS_DISPLAY

@st.fragment
def render_bookings_tab(booking_service):
    """РАСШИРЕННАЯ вкладка управления записями"""
    st.markdown("""
    <h3 style="color: #225c52; font-size: 1.4rem; font-weight: 600; 
         margin-bottom: 1.25rem; padding-bottom: 0.75rem; 
         border-bottom: 2px solid rgba(136, 200, 188, 0.2);">
        📋 Управление записями
    </h3>
    """, unsafe_allow_html=True)
    st.caption("Всё время — по Москве (MSK)")
    
    # Кнопка создания заказа
    col_title, col_btn = st.columns([4, 1])
    with col_btn:
        if st.button("➕ Создать заказ", use_container_width=True, type="primary", key="new_booking_btn_records"):
            st.session_state.show_new_booking_form_records = not st.session_state.get('show_new_booking_form_records', False)
    
    # Форма создания заказа
    if st.session_state.get('show_new_booking_form_records'):
        from services.client_service import ClientService
        client_service = ClientService()
        render_new_booking_form_with_product(client_service, booking_service, "records")
        st.markdown("---")
    
    # Используем fragment для фильтров
    render_bookings_with_filters(booking_service)

@st.fragment
def render_new_booking_form_with_product(client_service, booking_service, form_key_suffix=""):
    """Форма создания заказа с выбором продукта"""
    st.markdown("### ➕ Создание нового заказа")
    
    with st.form(f"new_booking_admin_form_{form_key_suffix}"):
        st.markdown("**👤 Клиент**")
        col_a, col_b = st.columns(2)
        
        with col_a:
            new_client_name = st.text_input("Имя *", placeholder="Иван Иванов", key=f"new_name_{form_key_suffix}")
            new_client_email = st.text_input("Email", placeholder="example@mail.com", key=f"new_email_{form_key_suffix}")
        
        with col_b:
            new_client_phone = st.text_input("Телефон *", placeholder="+7 (999) 123-45-67", key=f"new_phone_{form_key_suffix}")
            new_client_telegram = st.text_input("Telegram", placeholder="@username", key=f"new_telegram_{form_key_suffix}")
        
        st.markdown("---")
        st.markdown("**📅 Детали записи**")
        
        col_c, col_d = st.columns(2)
        
        with col_c:
            booking_date = st.date_input("Дата *", min_value=now_msk().date(), 
                                       max_value=now_msk().date() + timedelta(days=30), key=f"booking_date_{form_key_suffix}")
        
        with col_d:
            booking_time = st.time_input("Время *", value=datetime.strptime("09:00", "%H:%M").time(), key=f"booking_time_{form_key_suffix}")
        
        booking_notes = st.text_area("Комментарий", height=80, placeholder="Причина обращения...", key=f"booking_notes_{form_key_suffix}")
        
        st.markdown("---")
        st.markdown("**💳 Продукт**")
        
        # Получаем продукты
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
                key=f"select_product_{form_key_suffix}"
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
            if form_key_suffix == "records":
                st.session_state.show_new_booking_form_records = False
            elif form_key_suffix == "profile":
                st.session_state.show_new_booking_form_profile = False
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
                    'status': 'pending_payment',
                    'is_admin': True
                }
                
                success, message = booking_service.create_booking(booking_data)
                
                if success:
                    # Сохраняем продукт если выбран
                    if selected_prod_id is not None:
                        try:
                            row = booking_service.get_booking_by_datetime(
                                new_client_phone, 
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
                    if form_key_suffix == "records":
                        st.session_state.show_new_booking_form_records = False
                    elif form_key_suffix == "profile":
                        st.session_state.show_new_booking_form_profile = False
                    st.rerun()
                else:
                    st.error(message)


@st.fragment
def render_bookings_with_filters(booking_service):
    """Fragment для фильтров и списка"""
    
    today = now_msk().date()
    date_from = today - timedelta(days=30)
    date_to = today + timedelta(days=30)
    
    try:
        all_bookings = booking_service.get_all_bookings(str(date_from), str(date_to))
        
        if not all_bookings.empty and 'status' in all_bookings.columns:
            total_count = len(all_bookings)
            pending_count = (all_bookings['status'] == 'pending_payment').sum()
            confirmed_count = (all_bookings['status'] == 'confirmed').sum()
            completed_count = (all_bookings['status'] == 'completed').sum()
            cancelled_count = (all_bookings['status'] == 'cancelled').sum()
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1: st.metric("📋 Всего", total_count)
            with col2: st.metric("🟡 Ожидают", pending_count)
            with col3: st.metric("✅ Подтверждены", confirmed_count)
            with col4: st.metric("✅ Завершены", completed_count)
            with col5: st.metric("❌ Отменены", cancelled_count)
    except Exception as e:
        st.warning(f"Не удалось загрузить статистику: {e}")
    
    st.markdown("---")
    
    col_f1, col_f2, col_f3 = st.columns([2, 2, 3])
    
    with col_f1:
        period_option = st.selectbox(
            "📅 Период",
            options=["custom", "today", "week", "month"],
            format_func=lambda x: {
                "custom": "Выбрать даты",
                "today": "Сегодня", 
                "week": "Эта неделя",
                "month": "Этот месяц"
            }[x],
            key="period_filter"
        )
        
        if period_option == "today":
            filter_from = today
            filter_to = today
        elif period_option == "week":
            filter_from = today - timedelta(days=today.weekday())
            filter_to = filter_from + timedelta(days=6)
        elif period_option == "month":
            filter_from = today.replace(day=1)
            next_month = today.replace(day=28) + timedelta(days=4)
            filter_to = next_month - timedelta(days=next_month.day)
        else:
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                filter_from = st.date_input("С", value=today, key="smart_from")
            with col_d2:
                filter_to = st.date_input("По", value=today + timedelta(days=7), key="smart_to")
    
    with col_f2:
        status_filter = st.selectbox(
            "🏷️ Статус",
            options=["all", "pending_payment", "confirmed", "completed", "cancelled"],
            format_func=lambda x: {
                "all": "📋 Все записи",
                "pending_payment": "🟡 Ожидают оплаты", 
                "confirmed": "✅ Подтверждённые",
                "completed": "✅ Завершённые",
                "cancelled": "❌ Отменённые"
            }[x],
            key="status_filter"
        )
    
    with col_f3:
        search_query = st.text_input(
            "🔍 Поиск", 
            placeholder="Имя, телефон или заметки...",
            key="smart_search"
        )
    
    try:
        df = booking_service.get_all_bookings(str(filter_from), str(filter_to))
        
        if not df.empty:
            if status_filter != "all":
                df = df[df['status'] == status_filter]
            
            if search_query:
                search_lower = search_query.lower()
                mask = (
                    df['client_name'].str.lower().str.contains(search_lower, na=False) |
                    df['client_phone'].str.lower().str.contains(search_lower, na=False) |
                    df['notes'].str.lower().str.contains(search_lower, na=False)
                )
                df = df[mask]
            
            df['booking_datetime'] = pd.to_datetime(df['booking_date'] + ' ' + df['booking_time'])
            df = df.sort_values('booking_datetime')
            
            st.markdown(f"### 📊 Найдено записей: {len(df)}")
            
            if len(df) > 0:
                dates = df['booking_date'].unique()
                prod_map = get_product_map()
                
                for date in sorted(dates):
                    date_bookings = df[df['booking_date'] == date]
                    st.markdown(f"#### 📅 {format_date(date)}")
                    
                    for _, booking in date_bookings.iterrows():
                        render_booking_card_fast(booking.to_dict(), booking_service, prod_map)
                    
                    st.markdown("---")
            else:
                st.info("🎉 Нет записей по выбранным фильтрам")
        else:
            st.info("📭 Нет записей для выбранного периода")
    except Exception as e:
        st.error(f"❌ Ошибка загрузки данных: {e}")


@st.fragment
def render_booking_card_fast(booking: dict, booking_service, prod_map: dict):
    """Карточка записи"""
    
    status_info = STATUS_DISPLAY.get(booking.get('status', 'confirmed'), STATUS_DISPLAY['confirmed'])
    is_pending = (booking.get('status') == 'pending_payment')
    is_active = (booking.get('status') in ['confirmed', 'pending_payment'])
    
    with st.container():
        col_info, col_actions = st.columns([4, 1])
        
        with col_info:
            st.markdown(f"""
            <div style="background: {status_info['bg_color']}; padding: 1rem; border-radius: 12px; 
                 border-left: 4px solid {status_info['color']}; margin-bottom: 0.5rem;">
                <p style="font-size: 1.1rem; font-weight: 600; margin: 0;">
                    {status_info['emoji']} {booking.get('booking_time', '')} — {booking.get('client_name', '')}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col_i1, col_i2 = st.columns([2, 1])
            
            with col_i1:
                st.text(f"📱 {booking.get('client_phone', '')}")
                if booking.get('notes'):
                    st.text(f"💭 {booking.get('notes')}")
            
            with col_i2:
                pid = booking.get('product_id')
                amount = booking.get('amount')
                
                if pid is not None and pid in prod_map:
                    pname = prod_map[pid].get('name') or f"ID {pid}"
                    st.text(f"🧾 {pname}")
                    if amount is not None:
                        st.text(f"💰 {amount} ₽")
                elif is_pending:
                    st.caption("💳 Продукт не выбран")
        
        with col_actions:
            booking_id = booking['id']
            
            if is_pending:
                if st.button("💳", key=f"pay_{booking_id}", 
                           help="Отметить как оплачено", 
                           use_container_width=True, type="primary"):
                    ok, msg = booking_service.mark_booking_paid(booking_id)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            
            if is_active:
                if st.button("❌", key=f"cancel_{booking_id}", 
                           help="Отменить запись", 
                           use_container_width=True):
                    ok, msg = booking_service.update_booking_status(booking_id, 'cancelled')
                    if ok:
                        st.success("✅ Отменено")
                        st.rerun()
                    else:
                        st.error(msg)
            
            with st.popover("⚙️", use_container_width=True):
                st.markdown("##### Дополнительно")
                
                new_status = st.selectbox(
                    "Статус",
                    options=['pending_payment', 'confirmed', 'completed', 'cancelled'],
                    format_func=lambda x: STATUS_DISPLAY[x]['text'],
                    index=['pending_payment', 'confirmed', 'completed', 'cancelled'].index(
                        booking.get('status', 'confirmed')
                    ),
                    key=f"status_{booking_id}"
                )
                
                if st.button("💾 Изменить статус", key=f"upd_status_{booking_id}", 
                           use_container_width=True):
                    ok, msg = booking_service.update_booking_status(booking_id, new_status)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                
                st.markdown("---")
                
                if st.button("🗑️ Удалить запись", key=f"del_{booking_id}", 
                           use_container_width=True, type="secondary"):
                    if booking_service.delete_booking(booking_id):
                        st.success("✅ Удалено")
                        st.rerun()
                    else:
                        st.error("❌ Ошибка удаления")