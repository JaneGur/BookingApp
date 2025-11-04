import streamlit as st

def render_stats_metrics(conf_cnt, compl_cnt, total_cnt):
    """Отрисовка метрик статистики"""
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.metric("Подтверждённые", int(conf_cnt))
    with c2: 
        st.metric("Завершённые", int(compl_cnt))
    with c3: 
        st.metric("Всего", int(total_cnt))

def render_client_stats(clients_df):
    """Отрисовка статистики клиентов"""
    if st.session_state.get('show_stats'):
        st.markdown("---")
        st.markdown("##### 📈 Быстрая статистика")
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        with stat_col1:
            st.metric("Всего клиентов", len(clients_df))
        with stat_col2:
            active_clients = len(clients_df[clients_df['upcoming_bookings'] > 0])
            st.metric("Активных", active_clients)
        with stat_col3:
            avg_bookings = clients_df['total_bookings'].mean()
            st.metric("Среднее записей", f"{avg_bookings:.1f}")
        with stat_col4:
            total_bookings = clients_df['total_bookings'].sum()
            st.metric("Всего записей", total_bookings)