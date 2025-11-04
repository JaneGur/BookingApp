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
from ..components.ui_components import render_stats_metrics  # Добавьте этот импорт

def render_bookings_tab(booking_service):
     """Вкладка управления записями"""
     st.markdown("""
    <h3 style="color: #225c52; font-size: 1.25rem; font-weight: 600; 
         margin-bottom: 1.25rem; padding-bottom: 0.75rem; 
         border-bottom: 2px solid rgba(136, 200, 188, 0.2);">
        📋 Управление записями
    </h3>
    """, unsafe_allow_html=True)
     st.caption("Всё время — по Москве (MSK)")
     inner_tabs = st.tabs(["📒 Записи", "🧾 Заказы"])

     with inner_tabs[0]:
        render_bookings_section(booking_service)
    
     with inner_tabs[1]:
        render_orders_section(booking_service)

def render_bookings_section(booking_service):
    """Секция записей"""
    today = now_msk().date()
    col_b1, col_b2 = st.columns([2, 1])
    with col_b1:
        date_from = st.date_input("С", value=today, key="adm_book_from")
    with col_b2:
        date_to = st.date_input("По", value=today + timedelta(days=30), key="adm_book_to")
    
    if st.button("🔄 Обновить", key="refresh_bookings", use_container_width=True):
        st.rerun()
    
    df = booking_service.get_all_bookings(str(date_from), str(date_to))
    # Показываем здесь только оплаченные записи
    if not df.empty and 'status' in df.columns:
        df = df[df['status'].isin(['confirmed','completed'])]
    
    # Поиск
    col_s1, = st.columns(1)
    with col_s1:
        search_q = st.text_input("Поиск (имя или телефон)", placeholder="Иван / +7", key="adm_book_search")
    if not df.empty and search_q:
        df = df[(df['client_name'].str.contains(search_q, case=False, na=False)) | (df['client_phone'].str.contains(search_q, case=False, na=False))]
    
    # Счётчики
    if not df.empty and 'status' in df.columns:
        conf_cnt = (df['status'] == 'confirmed').sum()
        compl_cnt = (df['status'] == 'completed').sum()
        from ..components.ui_components import render_stats_metrics
        render_stats_metrics(conf_cnt, compl_cnt, len(df))
    
    if not df.empty:
        st.info(f"📊 Найдено записей: {len(df)}")
        df['booking_date'] = pd.to_datetime(df['booking_date']).dt.strftime('%d.%m.%Y')
        for date in sorted(df['booking_date'].unique()):
            st.markdown(f"#### 📅 {date}")
            date_bookings = df[df['booking_date'] == date]
            for _, row in date_bookings.iterrows():
                render_booking_card(row)
            st.markdown("---")
    else:
        st.info("📭 Нет записей для выбранного периода")

def render_orders_section(booking_service):
    """Секция заказов"""
    st.caption("Всё время — по Москве (MSK)")
    today = now_msk().date()
    col_o1, col_o2, col_o3 = st.columns([1,1,1])
    with col_o1:
        od_from = st.date_input("С", value=today, key="adm_order_from")
    with col_o2:
        od_to = st.date_input("По", value=today + timedelta(days=30), key="adm_order_to")
    with col_o3:
        status_filter = st.selectbox("Статус", ["Ожидают оплаты","Оплаченные","Все"], index=0, key="adm_order_status")

    try:
        supabase = db_manager.get_client()
        resp_all = supabase.table('bookings').select('*')\
            .gte('booking_date', str(od_from))\
            .lte('booking_date', str(od_to))\
            .neq('status','cancelled')\
            .order('booking_date').order('booking_time').execute()
        all_orders = resp_all.data or []
        pending_count = sum(1 for o in all_orders if o.get('status') == 'pending_payment')
        paid_count = sum(1 for o in all_orders if o.get('status') in ('confirmed','completed'))
        
        c1,c2,c3 = st.columns(3)
        with c1: st.metric("Ожидают оплаты", pending_count)
        with c2: st.metric("Оплаченные", paid_count)
        with c3: st.metric("Всего", len(all_orders))

        if status_filter == "Ожидают оплаты":
            orders = [o for o in all_orders if o.get('status') == 'pending_payment']
        elif status_filter == "Оплаченные":
            orders = [o for o in all_orders if o.get('status') in ('confirmed','completed')]
        else:
            orders = all_orders
        
        # Поиск по имени/телефону
        search_orders = st.text_input("Поиск (имя или телефон)", placeholder="Иван / +7", key="adm_order_search")
        if search_orders:
            q = search_orders.lower()
            def hit(o):
                return (str(o.get('client_name','')).lower().find(q) != -1) or (str(o.get('client_phone','')).lower().find(q) != -1)
            orders = [o for o in orders if hit(o)]
        
        prod_map = get_product_map()
        
        if orders:
            for b in orders:
                with st.expander(f"{format_date(b.get('booking_date',''))} {b.get('booking_time','')} — {b.get('client_name','')}"):
                    render_order_details(b, booking_service, prod_map)
        else:
            st.info("Нет заказов для выбранного фильтра")
            
    except Exception as e:
        st.warning(f"⚠️ Не удалось получить заказы: {e}")