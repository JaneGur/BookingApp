import streamlit as st
import pandas as pd
from services.analytics_service import AnalyticsService
from datetime import timedelta
from utils.datetime_helpers import now_msk

def render_analytics_tab(analytics_service):
    
    """Вкладка аналитики"""
    
    st.markdown("""
    <h3 style="color: #225c52; font-size: 1.4rem; font-weight: 600; 
         margin-bottom: 1.25rem; padding-bottom: 0.75rem; 
         border-bottom: 2px solid rgba(136, 200, 188, 0.2);">
        📊 Аналитика
    </h3>
    """, unsafe_allow_html=True)
    
    total, upcoming, this_month, this_week = analytics_service.get_stats()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 Всего", total)
    col2.metric("⏰ Предстоящих", upcoming)
    col3.metric("📅 За месяц", this_month)
    col4.metric("📆 За неделю", this_week)

    st.markdown("---")
    st.markdown("#### 🧾 Сводка по продуктам")
    render_product_summary(analytics_service)

def render_product_summary(analytics_service):
    """Сводка по продуктам"""
    today = now_msk().date()
    default_from = (today - timedelta(days=30))
    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        date_from = st.date_input("С даты", value=default_from)
    with c2:
        date_to = st.date_input("По дату", value=today)
    with c3:
        status_opts = {
            'pending_payment': '🟡 Ожидает оплаты',
            'confirmed': '✅ Подтверждена',
            'completed': '✅ Завершена',
            'cancelled': '❌ Отменена',
        }
        chosen_statuses = st.multiselect(
            "Статусы",
            options=list(status_opts.keys()),
            default=['confirmed','completed'],
            format_func=lambda x: status_opts[x]
        )
    
    df = analytics_service.get_product_summary(
        date_from=str(date_from),
        date_to=str(date_to),
        statuses=chosen_statuses
    )
    
    if not df.empty:
        # Берём только нужные колонки в исходных именах, затем форматируем и переименовываем
        cols = [c for c in ['product_name','count','revenue'] if c in df.columns]
        df_show = df[cols].copy()
        if 'revenue' in df_show.columns:
            df_show['revenue'] = df_show['revenue'].map(lambda x: f"{x:,.2f}".replace(',', ' ').replace('.', ','))
        df_show = df_show.rename(columns={
            'product_name': 'Продукт',
            'count': 'Кол-во',
            'revenue': 'Выручка, ₽'
        })
        st.dataframe(df_show, use_container_width=True)
        total_count = int(df['count'].sum()) if 'count' in df.columns else 0
        total_rev = float(df['revenue'].sum()) if 'revenue' in df.columns else 0.0
        st.markdown(f"**Итого:** {total_count} заказов · {total_rev:,.2f} ₽".replace(',', ' ').replace('.', ','))
    else:
        st.info("Данных по продуктам за выбранный период нет")