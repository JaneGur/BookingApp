import streamlit as st
import pandas as pd
from datetime import timedelta
from services.booking_service import BookingService
from ui.components import render_booking_card
from utils.datetime_helpers import now_msk
from core.database import db_manager
from utils.formatters import format_date
from utils.product_cache import get_product_map
from ..components.booking_components import render_order_details
from ..components.ui_components import render_stats_metrics
from config.constants import STATUS_DISPLAY

def render_bookings_tab(booking_service):
    """Улучшенная вкладка управления записями - единый интерфейс"""
    st.markdown("""
    <h3 style="color: #225c52; font-size: 1.25rem; font-weight: 600; 
         margin-bottom: 1.25rem; padding-bottom: 0.75rem; 
         border-bottom: 2px solid rgba(136, 200, 188, 0.2);">
        📋 Управление записями
    </h3>
    """, unsafe_allow_html=True)
    st.caption("Всё время — по Москве (MSK)")
    
    # Единый интерфейс со смарт-фильтрами
    render_unified_bookings(booking_service)

def render_unified_bookings(booking_service):
    """Унифицированный интерфейс записей и заказов"""
    
    # 1. СТАТИСТИКА В ШАПКЕ
    today = now_msk().date()
    date_from = today - timedelta(days=30)
    date_to = today + timedelta(days=30)
    
    try:
        # Получаем все записи для статистики
        all_bookings = booking_service.get_all_bookings(str(date_from), str(date_to))
        
        if not all_bookings.empty and 'status' in all_bookings.columns:
            total_count = len(all_bookings)
            pending_count = (all_bookings['status'] == 'pending_payment').sum()
            confirmed_count = (all_bookings['status'] == 'confirmed').sum()
            completed_count = (all_bookings['status'] == 'completed').sum()
            cancelled_count = (all_bookings['status'] == 'cancelled').sum()
            
            # Отображаем метрики
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("📋 Всего", total_count)
            with col2:
                st.metric("🟡 Ожидают", pending_count, delta=None)
            with col3:
                st.metric("✅ Подтверждены", confirmed_count)
            with col4:
                st.metric("✅ Завершены", completed_count)
            with col5:
                st.metric("❌ Отменены", cancelled_count)
    except Exception as e:
        st.warning(f"Не удалось загрузить статистику: {e}")

    # 2. БЫСТРЫЕ ФИЛЬТРЫ В ОДНУ СТРОКУ
    st.markdown("---")
    
    col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 3, 1])
    
    with col_f1:
        # Фильтр периода
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
            # Кастомный выбор дат
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                filter_from = st.date_input("С", value=today, key="smart_from")
            with col_d2:
                filter_to = st.date_input("По", value=today + timedelta(days=7), key="smart_to")
    
    with col_f2:
        # Фильтр статуса
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
        # Поиск
        search_query = st.text_input(
            "🔍 Поиск", 
            placeholder="Имя, телефон или заметки...",
            key="smart_search"
        )
    
    with col_f4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Обновить", use_container_width=True):
            st.rerun()

    # 3. ПОЛУЧЕНИЕ И ФИЛЬТРАЦИЯ ДАННЫХ
    try:
        # Получаем данные
        df = booking_service.get_all_bookings(str(filter_from), str(filter_to))
        
        if not df.empty:
            # Применяем фильтр статуса
            if status_filter != "all":
                df = df[df['status'] == status_filter]
            
            # Применяем поиск
            if search_query:
                search_lower = search_query.lower()
                mask = (
                    df['client_name'].str.lower().str.contains(search_lower, na=False) |
                    df['client_phone'].str.lower().str.contains(search_lower, na=False) |
                    df['notes'].str.lower().str.contains(search_lower, na=False)
                )
                df = df[mask]
            
            # Сортируем по дате и времени
            df['booking_datetime'] = pd.to_datetime(df['booking_date'] + ' ' + df['booking_time'])
            df = df.sort_values('booking_datetime')
            
            # 4. ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ С ГРУППИРОВКОЙ ПО ДАТАМ
            st.markdown(f"### 📊 Найдено записей: {len(df)}")
            
            if len(df) > 0:
                # Группируем по датам
                dates = df['booking_date'].unique()
                
                for date in sorted(dates):
                    date_bookings = df[df['booking_date'] == date]
                    
                    # Заголовок даты
                    st.markdown(f"#### 📅 {format_date(date)}")
                    
                    # Отображаем карточки для этой даты
                    for _, booking in date_bookings.iterrows():
                        render_smart_booking_card(booking.to_dict(), booking_service, get_product_map())
                    
                    st.markdown("---")
            else:
                st.info("🎉 Нет записей по выбранным фильтрам")
                
        else:
            st.info("📭 Нет записей для выбранного периода")
            
    except Exception as e:
        st.error(f"❌ Ошибка загрузки данных: {e}")

def render_smart_booking_card(booking: dict, booking_service, prod_map: dict):
    """Умная карточка записи с быстрыми действиями"""
    
    status_info = STATUS_DISPLAY.get(booking.get('status', 'confirmed'), STATUS_DISPLAY['confirmed'])
    
    # Определяем доступные действия в зависимости от статуса
    is_pending = (booking.get('status') == 'pending_payment')
    is_active = (booking.get('status') in ['confirmed', 'pending_payment'])
    
    # Основная карточка
    with st.container():
        col_info, col_actions = st.columns([4, 1])
        
        with col_info:
            # Заголовок со статусом
            st.markdown(f"""
            <div style="background: {status_info['bg_color']}; padding: 1rem; border-radius: 12px; 
                 border-left: 4px solid {status_info['color']}; margin-bottom: 0.5rem;">
                <p style="font-size: 1.1rem; font-weight: 600; margin: 0;">
                    {status_info['emoji']} {booking.get('booking_time', '')} — {booking.get('client_name', '')}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Информация
            col_i1, col_i2 = st.columns([2, 1])
            
            with col_i1:
                st.text(f"📱 {booking.get('client_phone', '')}")
                
                if booking.get('notes'):
                    st.text(f"💭 {booking.get('notes')}")
            
            with col_i2:
                # Продукт и сумма
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
            # Действия в зависимости от статуса
            if is_pending:
                # Кнопка оплаты
                if st.button("💳", key=f"pay_{booking['id']}", 
                           help="Отметить как оплачено", 
                           use_container_width=True, type="primary"):
                    with st.spinner("Обработка..."):
                        ok, msg = booking_service.mark_booking_paid(booking['id'])
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            
            if is_active:
                # Кнопка отмены
                if st.button("❌", key=f"cancel_{booking['id']}", 
                           help="Отменить запись", 
                           use_container_width=True):
                    with st.spinner("Отмена..."):
                        ok, msg = booking_service.update_booking_status(booking['id'], 'cancelled')
                        if ok:
                            st.success("✅ Отменено")
                            st.rerun()
                        else:
                            st.error(msg)
            
            # Кнопка удаления (всегда доступна)
            with st.popover("⚙️", use_container_width=True):
                st.markdown("##### Дополнительно")
                
                # Изменить статус
                new_status = st.selectbox(
                    "Статус",
                    options=['pending_payment', 'confirmed', 'completed', 'cancelled'],
                    format_func=lambda x: STATUS_DISPLAY[x]['text'],
                    index=['pending_payment', 'confirmed', 'completed', 'cancelled'].index(booking.get('status', 'confirmed')),
                    key=f"status_{booking['id']}"
                )
                
                if st.button("💾 Изменить статус", key=f"upd_status_{booking['id']}", use_container_width=True):
                    ok, msg = booking_service.update_booking_status(booking['id'], new_status)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                
                st.markdown("---")
                
                # Удалить
                if st.button("🗑️ Удалить запись", key=f"del_{booking['id']}", 
                           use_container_width=True, type="secondary"):
                    if booking_service.delete_booking(booking['id']):
                        st.success("✅ Удалено")
                        st.rerun()
                    else:
                        st.error("❌ Ошибка удаления")

