import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from services.booking_service import BookingService
from services.client_service import ClientService
from services.analytics_service import AnalyticsService
from services.settings_service import SettingsService
from services.notification_service import NotificationService
from ui.components import render_booking_card, render_info_panel
from utils.formatters import format_date
from core.database import db_manager
from utils.product_cache import get_product_map
from core.auth import AuthManager
from utils.datetime_helpers import now_msk, combine_msk

def render_admin_panel():
    """Отрисовка панели администратора"""
    st.title("👩‍💼 Панель управления")
    
    booking_service = BookingService()
    client_service = ClientService()
    analytics_service = AnalyticsService()
    settings_service = SettingsService()
    notification_service = NotificationService()
    
    tabs = st.tabs(["📋 Записи", "👥 Клиенты", "⚙️ Настройки", "🚫 Блокировки", "📊 Аналитика", "🔔 Уведомления", "💳 Продукты", "📄 Документы"])
    
    with tabs[0]:
        render_bookings_tab(booking_service)
    
    with tabs[1]:
        render_clients_tab(client_service, booking_service)
    
    with tabs[2]:
        render_settings_tab(settings_service)
    
    with tabs[3]:
        render_blocking_tab()
    
    with tabs[4]:
        render_analytics_tab(analytics_service)
    
    with tabs[5]:
        render_notifications_tab(notification_service)

    with tabs[6]:
        render_products_tab()

    with tabs[7]:
        render_documents_tab()

def render_bookings_tab(booking_service):
    """Вкладка управления записями"""
    st.markdown("### 📋 Управление")
    st.caption("Всё время — по Москве (MSK)")
    inner_tabs = st.tabs(["📒 Записи", "🧾 Заказы"])

    # ===== 📒 ЗАПИСИ =====
    with inner_tabs[0]:
        today = now_msk().date()
        col_b1, col_b2 = st.columns([2, 1])
        with col_b1:
            date_from = st.date_input("С", value=today, key="adm_book_from")
        with col_b2:
            date_to = st.date_input("По", value=today + timedelta(days=30), key="adm_book_to")
        if st.button("🔄 Обновить", key="refresh_bookings", width='stretch'):
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
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Подтверждённые", int(conf_cnt))
            with c2: st.metric("Завершённые", int(compl_cnt))
            with c3: st.metric("Всего", int(len(df)))
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

    # ===== 🧾 ЗАКАЗЫ =====
    with inner_tabs[1]:
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
        except Exception as e:
            orders = []
            prod_map = {}
            st.warning(f"⚠️ Не удалось получить заказы: {e}")

        if orders:
            for b in orders:
                with st.expander(f"{format_date(b.get('booking_date',''))} {b.get('booking_time','')} — {b.get('client_name','')}"):
                    colp1, colp2, colp3 = st.columns([2,1,1])
                    with colp1:
                        st.write(f"Телефон: {b.get('client_phone','')}")
                        if b.get('notes'):
                            st.info(f"💭 {b.get('notes')}")
                        if b.get('product_id') is not None or b.get('amount') is not None:
                            pid = b.get('product_id')
                            if pid is not None and pid in prod_map:
                                pname = prod_map[pid].get('name') or f"ID {pid}"
                            else:
                                pname = f"ID {pid}" if pid is not None else '—'
                            amount = b.get('amount')
                            st.write(f"Продукт: {pname}{(f', Сумма: {amount} ₽' if amount is not None else '')}")
                        if b.get('status') in ('confirmed','completed'):
                            try:
                                consult_dt = combine_msk(b.get('booking_date',''), b.get('booking_time',''))
                                reminder_dt = consult_dt - timedelta(hours=1)
                                from services.notification_service import NotificationService
                                ns = NotificationService()
                                chat_id = ns.get_client_telegram_chat_id(b.get('client_phone',''))
                                client_state = "подключен" if chat_id else "не подключен"
                                st.caption(f"⏰ Напоминание планируется на {reminder_dt.strftime('%d.%m.%Y %H:%M')} · Telegram клиента: {client_state}")
                            except Exception:
                                pass
                    with colp2:
                        status_val = b.get('status')
                        if status_val == 'pending_payment':
                            if st.button("💳 Пометить как оплачено", key=f"pending_paid_{b['id']}", width='stretch'):
                                ok, msg = booking_service.mark_booking_paid(b['id'])
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                        # Для заказов в статусе оплачено напоминания в этом разделе не показываем
                    with colp3:
                        if st.button("❌ Отменить заказ", key=f"pending_cancel_{b['id']}", width='stretch'):
                            ok, msg = booking_service.update_booking_status(b['id'], 'cancelled')
                            if ok:
                                st.success("✅ Отменено")
                                st.rerun()
                            else:
                                st.error(msg)
        else:
            st.info("Нет заказов для выбранного фильтра")

    

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
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn1:
        if st.button("🔄 Обновить список", width='stretch', key="refresh_clients"):
            st.rerun()
    with col_btn2:
        if st.button("📊 Статистика", width='stretch', key="toggle_stats"):
            st.session_state.show_stats = not st.session_state.get('show_stats', False)
    with col_btn3:
        if st.button("➕ Новая запись", width='stretch', type="primary", key="new_booking_btn"):
            st.session_state.show_new_booking_form = True
    
    # Форма создания новой записи
    if st.session_state.get('show_new_booking_form'):
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
            # Плашка с продуктом по умолчанию (featured) — только как подсказка, админ может выбрать другой
            try:
                from core.database import db_manager
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
                submit_booking = st.form_submit_button("✅ Создать заказ", width='stretch')
            with col_cancel:
                if st.form_submit_button("❌ Отмена", width='stretch'):
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
        
        # Отображаем клиентов
        for idx, client in clients_df.iterrows():
            with st.expander(f"👤 {client['client_name']} - 📱 {client['client_phone']} | 📅 Записей: {client['total_bookings']}", expanded=False):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown("**Контактная информация:**")
                    st.write(f"📧 Email: {client['client_email'] or 'Не указан'}")
                    st.write(f"💬 Telegram: {client['client_telegram'] or 'Не указан'}")
                    
                    st.markdown("**Статистика:**")
                    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                    with col_stat1:
                        st.metric("Всего записей", client['total_bookings'])
                    with col_stat2:
                        st.metric("Предстоящие", client['upcoming_bookings'])
                    with col_stat3:
                        st.metric("Завершено", client['completed_bookings'])
                    with col_stat4:
                        st.metric("Отменено", client['cancelled_bookings'])
                
                with col2:
                    st.markdown("**Даты:**")
                    if client['first_booking']:
                        first_booking = format_date(client['first_booking'])
                        st.write(f"📅 Первая запись: {first_booking}")
                    if client['last_booking']:
                        last_booking = format_date(client['last_booking'])
                        st.write(f"📅 Последняя запись: {last_booking}")
                
                with col3:
                    if st.button("📋 История записей", key=f"history_{client['phone_hash']}", width='stretch'):
                        st.session_state.selected_client = client['phone_hash']
                        st.session_state.selected_client_name = client['client_name']
                    # Удаление клиента
                    with st.popover("🗑️ Удалить клиента", use_container_width=True):
                        st.warning("Действие необратимо. Удаляется профиль и доступ. Можно также удалить ВСЕ записи клиента.")
                        cascade = st.checkbox("Также удалить все записи клиента", key=f"del_cascade_{client['phone_hash']}")
                        confirm = st.checkbox("Я понимаю, удалить без возможности восстановления", key=f"del_confirm_ack_{client['phone_hash']}")
                        disabled = not confirm
                        if st.button("✅ Подтвердить удаление", key=f"del_exec_{client['phone_hash']}", use_container_width=True, disabled=disabled):
                            ok, msg = client_service.delete_client_by_hash(client['phone_hash'], cascade_bookings=cascade)
                            if ok:
                                st.success(msg)
                                st.session_state.selected_client = None
                                st.rerun()
                            else:
                                st.error(msg)
                
                # История записей выбранного клиента
                if st.session_state.get('selected_client') == client['phone_hash']:
                    st.markdown("---")
                    st.markdown(f"#### 📋 История записей: {client['client_name']}")
                    
                    history_df = client_service.get_client_booking_history(client['phone_hash'])
                    if not history_df.empty:
                        for _, booking in history_df.iterrows():
                            render_client_booking_history(booking, booking_service)
                    else:
                        st.info("📭 История записей пуста")
        
        # Сводная статистика по всем клиентам
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
            
    else:
        st.info("📭 В базе нет клиентов")

def render_client_booking_history(booking, booking_service):
    """Отрисовка истории записей клиента"""
    from config.constants import STATUS_DISPLAY
    status_info = STATUS_DISPLAY.get(booking['status'], STATUS_DISPLAY['confirmed'])
    
    with st.container():
        col_hist1, col_hist2, col_hist3 = st.columns([3, 1, 1])
        
        with col_hist1:
            date_formatted = format_date(booking['booking_date'])
            st.write(f"**{date_formatted} {booking['booking_time']}** - {status_info['emoji']} {status_info['text']}")
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
        
        with col_hist2:
            if booking.get('created_at'):
                created_at_value = booking['created_at']
                # Поддержка как ISO-дат со временем (YYYY-MM-DDTHH:MM:SS), так и дат без времени (YYYY-MM-DD)
                created_at = format_date(created_at_value[:10]) if 'T' in created_at_value else format_date(created_at_value)
                st.write(f"📅 Записано: {created_at}")
        
        with col_hist3:
            # Меню управления записью
            with st.popover("⚙️ Управление", width='stretch'):
                # Изменение статуса
                st.markdown("**📊 Изменить статус:**")
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
                    key=f"status_{booking['id']}"
                )
                if st.button("🔄 Обновить статус", key=f"update_status_{booking['id']}", width='stretch'):
                    success, message = booking_service.update_booking_status(booking['id'], new_status)
                    if success:
                        st.success(message)
                        st.rerun()
                if st.button("💳 Пометить как оплачено", key=f"mark_paid_{booking['id']}", width='stretch'):
                    success, message = BookingService().mark_booking_paid(booking['id'])
                    if success:
                        st.success(message)
                        st.rerun()

                st.markdown("**🗓️ Изменить дату и время:**")
                from datetime import datetime
                cur_date = booking['booking_date']
                cur_time = booking['booking_time']
                try:
                    date_val = datetime.strptime(cur_date, "%Y-%m-%d").date()
                except Exception:
                    try:
                        date_val = datetime.strptime(cur_date[:10], "%Y-%m-%d").date()
                    except Exception:
                        date_val = now_msk().date()
                try:
                    time_val = datetime.strptime(cur_time, "%H:%M").time() if cur_time else datetime.strptime("09:00", "%H:%M").time()
                except Exception:
                    time_val = datetime.strptime("09:00", "%H:%M").time()
                new_date = st.date_input("Дата", value=date_val, key=f"edit_date_{booking['id']}")
                new_time = st.time_input("Время", value=time_val, key=f"edit_time_{booking['id']}")

                st.markdown("**💭 Комментарий:**")
                new_notes = st.text_area("Комментарий", value=booking['notes'] or '', height=80, key=f"edit_notes_{booking['id']}")
                if st.button("💾 Сохранить изменения", key=f"save_changes_{booking['id']}", width='stretch'):
                    ok, msg = booking_service.update_booking_details(
                        booking['id'],
                        new_date=str(new_date),
                        new_time=new_time.strftime("%H:%M") if new_time else None,
                        new_notes=new_notes
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        
        st.markdown("---")

def render_documents_tab():
    """Загрузка и управление документами (политика, оферты и пр.)"""
    st.markdown("### 📄 Документы")
    sb_read = db_manager.get_client()
    sb_write = db_manager.get_service_client()
    if sb_read is None:
        st.error("❌ Нет подключения к базе данных")
        return
    st.markdown("#### ⬆️ Загрузить документ")
    with st.form("upload_doc_form"):
        colu1, colu2 = st.columns([2,1])
        with colu1:
            title = st.text_input("Название документа", placeholder="Политика конфиденциальности")
        with colu2:
            doc_type = st.selectbox("Тип", ["policy", "offer", "other"], index=0)
        file = st.file_uploader("Файл", type=["pdf", "doc", "docx", "txt", "rtf"], accept_multiple_files=False)
        up_submit = st.form_submit_button("📤 Загрузить", width='stretch')
    if up_submit:
        if not file or not title:
            st.error("❌ Укажите название и выберите файл")
        else:
            import uuid
            ext = (file.name.split(".")[-1] or "bin").lower()
            key = f"{uuid.uuid4().hex}.{ext}"
            try:
                bucket = sb_write.storage.from_("public_docs") if sb_write else None
                # Некоторые версии клиента ожидают snake_case ключи и строковый upsert
                if bucket is None:
                    raise Exception("service client is not configured")
                bucket.upload(key, file.getvalue(), {"content_type": (file.type or "application/octet-stream"), "upsert": "true"})
                public_url = bucket.get_public_url(key)
            except Exception as e:
                st.error(f"❌ Хранилище недоступно или не создано: {e}")
                with st.expander("📄 Инструкция по созданию bucket public_docs", expanded=False):
                    st.code(
                        """
                        -- Выполните в Supabase SQL (Storage):
                        -- В разделе Storage создайте bucket с именем public_docs и включите Public.
                        -- Затем перезапустите приложение.
                        """,
                        language="sql"
                    )
                public_url = None
            if public_url:
                try:
                    (sb_write or sb_read).table('documents').insert({
                        'title': title.strip(),
                        'doc_type': doc_type,
                        'filename': file.name,
                        'storage_key': key,
                        'url': public_url,
                        'is_active': True,
                        'created_at': now_msk().isoformat(),
                        'updated_at': now_msk().isoformat()
                    }).execute()
                    st.success("✅ Документ загружен")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Ошибка записи в таблицу documents: {e}")
                    with st.expander("📄 Инструкция по созданию таблицы documents", expanded=False):
                        st.code(
                            """
                            CREATE TABLE IF NOT EXISTS documents (
                              id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                              title TEXT NOT NULL,
                              doc_type TEXT,
                              filename TEXT,
                              storage_key TEXT,
                              url TEXT,
                              is_active BOOLEAN DEFAULT TRUE,
                              created_at TIMESTAMPTZ DEFAULT NOW(),
                              updated_at TIMESTAMPTZ DEFAULT NOW()
                            );
                            CREATE INDEX IF NOT EXISTS documents_active_idx ON documents(is_active);
                            """,
                            language="sql"
                        )
    st.markdown("---")
    st.markdown("#### 📚 Список документов")
    try:
        rows = sb_read.table('documents').select('*').order('created_at', desc=True).execute().data or []
    except Exception as e:
        rows = []
        st.error(f"❌ Не удалось получить список документов: {e}")
    if not rows:
        st.info("Документы отсутствуют")
        return
    for d in rows:
        with st.expander(f"{d.get('title')} — {d.get('doc_type','other')}", expanded=False):
            st.write(f"Файл: {d.get('filename','—')}")
            if d.get('url'):
                st.link_button("Открыть", url=d['url'], width='stretch')
            col_da, col_db = st.columns([1,1])
            with col_da:
                new_active = st.checkbox("Активен", value=bool(d.get('is_active')), key=f"doc_active_{d['id']}")
                if st.button("💾 Сохранить", key=f"doc_save_{d['id']}", width='stretch'):
                    try:
                        (sb_write or sb_read).table('documents').update({'is_active': new_active, 'updated_at': now_msk().isoformat()}).eq('id', d['id']).execute()
                        st.success("✅ Сохранено")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Ошибка сохранения: {e}")
            with col_db:
                if st.button("🗑️ Удалить", key=f"doc_del_{d['id']}", width='stretch'):
                    try:
                        # Пытаемся удалить файл из хранилища
                        if d.get('storage_key'):
                            try:
                                (sb_write or sb_read).storage.from_("public_docs").remove([d['storage_key']])
                            except Exception:
                                pass
                        (sb_write or sb_read).table('documents').delete().eq('id', d['id']).execute()
                        st.success("✅ Удалено")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Ошибка удаления: {e}")

def render_settings_tab(settings_service):
    """Вкладка настроек"""
    st.markdown("### ⚙️ Настройки системы")
    
    settings_tabs = st.tabs(["📅 Расписание", "ℹ️ Информационная панель", "🔐 Безопасность"])
    
    with settings_tabs[0]:
        render_schedule_settings(settings_service)
    
    with settings_tabs[1]:
        render_info_settings(settings_service)

    with settings_tabs[2]:
        render_security_settings()

def render_schedule_settings(settings_service):
    """Настройки расписания"""
    st.markdown("#### 📅 Настройки расписания")
    
    settings = settings_service.get_settings()
    if settings:
        col1, col2, col3 = st.columns(3)
        with col1:
            work_start = st.time_input("🕐 Начало рабочего дня", 
                                     value=datetime.strptime(settings.work_start, '%H:%M').time())
        with col2:
            work_end = st.time_input("🕐 Конец рабочего дня", 
                                   value=datetime.strptime(settings.work_end, '%H:%M').time())
        with col3:
            session_duration = st.number_input("⏱️ Длительность сессии (мин)", 
                                              min_value=15, max_value=180, 
                                              value=settings.session_duration, step=15)
        # Подсказка: последняя сессия начинается не позже (work_end - duration)
        try:
            from datetime import datetime as _dt, timedelta as _td
            today = _dt.combine(now_msk().date(), work_end)
            last_start_dt = today - _td(minutes=int(session_duration))
            st.caption(f"Последняя сессия должна начинаться не позже: {last_start_dt.strftime('%H:%M')}")
            # Валидация: интервал дня должен быть >= длительности
            start_dt = _dt.combine(now_msk().date(), work_start)
            if last_start_dt < start_dt:
                st.error("Длительность сессии больше рабочего интервала. Уменьшите длительность или сдвиньте границы дня.")
                save_allowed = False
            else:
                save_allowed = True
        except Exception:
            save_allowed = True
        
        if st.button("💾 Сохранить настройки расписания", width='stretch', disabled=not save_allowed):
            update_data = {
                'work_start': work_start.strftime('%H:%M'),
                'work_end': work_end.strftime('%H:%M'),
                'session_duration': session_duration
            }
            
            if settings_service.update_settings(update_data):
                st.success("✅ Настройки расписания сохранены!")
                st.rerun()
            else:
                st.error("❌ Ошибка сохранения настроек расписания")

def render_info_settings(settings_service):
    """Настройки информационной панели"""
    st.markdown("#### ℹ️ Настройки информационной панели")
    st.info("Здесь вы можете редактировать текст, который видят клиенты в правой панели")
    
    settings = settings_service.get_settings()
    if settings:
        with st.form("info_panel_settings"):
            st.markdown("**Основные настройки:**")
            info_title = st.text_input("📝 Заголовок панели", 
                                     value=settings.info_title)
            
            st.markdown("**📋 Содержимое панели:**")
            info_work_hours = st.text_area("🕐 Рабочее время", 
                                         value=settings.info_work_hours,
                                         height=80,
                                         help="Используйте \\n для переноса строк")
            
            info_session_duration = st.text_area("⏱️ Длительность консультации", 
                                               value=settings.info_session_duration,
                                               height=80)
            
            info_format = st.text_area("💻 Формат консультации", 
                                     value=settings.info_format,
                                     height=80)
            
            info_contacts = st.text_area("📞 Контактная информация", 
                                       value=settings.info_contacts,
                                       height=100,
                                       help="Укажите телефоны, email, сайт и другие контакты")
            
            info_additional = st.text_area("📝 Дополнительная информация", 
                                         value=settings.info_additional,
                                         height=100,
                                         placeholder="Любая дополнительная информация для клиентов...",
                                         help="Необязательное поле")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submit_info = st.form_submit_button("💾 Сохранить настройки", width='stretch')
            with col2:
                preview_info = st.form_submit_button("👁️ Предпросмотр", width='stretch')
            
            if submit_info:
                info_data = {
                    'info_title': info_title,
                    'info_work_hours': info_work_hours,
                    'info_session_duration': info_session_duration,
                    'info_format': info_format,
                    'info_contacts': info_contacts,
                    'info_additional': info_additional
                }
                
                if settings_service.update_settings(info_data):
                    st.success("✅ Настройки информационной панели сохранены!")
                    st.rerun()
                else:
                    st.error("❌ Ошибка сохранения настроек.")
            
            if preview_info:
                st.markdown("---")
                st.markdown("#### 👁️ Предпросмотр информационной панели")
                render_info_panel()

def render_security_settings():
    st.markdown("#### 🔐 Смена пароля администратора")
    with st.form("admin_change_password_form"):
        col1, col2 = st.columns(2)
        with col1:
            current_pwd = st.text_input("Текущий пароль", type="password")
            new_pwd = st.text_input("Новый пароль", type="password")
        with col2:
            confirm_pwd = st.text_input("Подтвердите новый пароль", type="password")
            show_info = st.checkbox("Показать пароль", value=False)
        if show_info:
            st.info(f"Новый пароль: {new_pwd}")
        submit = st.form_submit_button("💾 Сменить пароль", width='stretch')

    if submit:
        if not current_pwd or not new_pwd or not confirm_pwd:
            st.error("❌ Заполните все поля")
            return
        if len(new_pwd) < 6:
            st.error("❌ Новый пароль должен быть не менее 6 символов")
            return
        if new_pwd != confirm_pwd:
            st.error("❌ Пароли не совпадают")
            return
        auth = AuthManager()
        if not auth.check_admin_password(current_pwd):
            st.error("❌ Неверный текущий пароль")
            return
        if auth.set_admin_password(new_pwd):
            try:
                ns = NotificationService()
                ns.bot.send_to_admin(f"🔐 Пароль администратора изменён\n🕒 {now_msk().strftime('%d.%m.%Y %H:%M:%S')}")
            except Exception:
                pass
            st.success("✅ Пароль администратора обновлён")
        else:
            st.error("❌ Не удалось обновить пароль администратора")

def render_blocking_tab():
    """Вкладка блокировок"""
    st.markdown("### 🚫 Управление блокировками")

    sb_read = db_manager.get_client()
    sb_write = db_manager.get_service_client()
    if sb_read is None:
        st.error("❌ Нет подключения к базе данных")
        return

    # Форма блокировки целого дня
    with st.form("block_day_form"):
        st.markdown("#### 📅 Заблокировать день")
        block_day_date = st.date_input(
            "Дата для блокировки",
            min_value=now_msk().date(),
            key="block_day_date",
        )
        reason_day = st.text_input("💬 Причина (необязательно)", placeholder="Отпуск, выходной, командировка…", key="block_day_reason")
        col1, col2 = st.columns([1, 1])
        with col1:
            submit_block_day = st.form_submit_button("🚫 Заблокировать день", width='stretch')
        with col2:
            cancel_block_day = st.form_submit_button("❌ Отмена", width='stretch')

        if submit_block_day:
            try:
                # Проверка дубликата
                existing = sb_read.table('blocked_slots')\
                    .select('id')\
                    .eq('block_date', str(block_day_date))\
                    .is_('block_time', None)\
                    .execute()
                if existing.data:
                    st.warning("⚠️ Такой день уже заблокирован")
                else:
                    payload = {
                        'block_date': str(block_day_date),
                        'block_time': None
                    }
                    if reason_day:
                        payload['reason'] = reason_day
                    try:
                        (sb_write or sb_read).table('blocked_slots').insert(payload).execute()
                    except Exception:
                        # Повтор без reason, если в БД нет такого столбца
                        (sb_write or sb_read).table('blocked_slots').insert({
                            'block_date': str(block_day_date),
                            'block_time': None
                        }).execute()
                    st.success("✅ День заблокирован")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Ошибка блокировки дня: {e}")

    st.markdown("---")

    # Форма блокировки конкретного слота
    with st.form("block_time_form"):
        st.markdown("#### 🕐 Заблокировать временной слот")
        col_dt1, col_dt2 = st.columns([1, 1])
        with col_dt1:
            block_time_date = st.date_input(
                "Дата",
                min_value=now_msk().date(),
                key="block_time_date",
            )
        with col_dt2:
            default_time = datetime.strptime("09:00", "%H:%M").time()
            block_time_time = st.time_input("Время", value=default_time, key="block_time_time")
        reason_time = st.text_input("💬 Причина (необязательно)", placeholder="Окно занято, личное дело…", key="block_time_reason")

        col_bt1, col_bt2 = st.columns([1, 1])
        with col_bt1:
            submit_block_time = st.form_submit_button("🚫 Заблокировать слот", width='stretch')
        with col_bt2:
            cancel_block_time = st.form_submit_button("❌ Отмена", width='stretch')

        if submit_block_time:
            try:
                time_str = block_time_time.strftime('%H:%M')
                # Проверка дубликата
                existing = sb_read.table('blocked_slots')\
                    .select('id')\
                    .eq('block_date', str(block_time_date))\
                    .eq('block_time', time_str)\
                    .execute()
                if existing.data:
                    st.warning("⚠️ Такой слот уже заблокирован")
                else:
                    payload = {
                        'block_date': str(block_time_date),
                        'block_time': time_str
                    }
                    if reason_time:
                        payload['reason'] = reason_time
                    try:
                        (sb_write or sb_read).table('blocked_slots').insert(payload).execute()
                    except Exception:
                        (sb_write or sb_read).table('blocked_slots').insert({
                            'block_date': str(block_time_date),
                            'block_time': time_str
                        }).execute()
                    st.success("✅ Слот заблокирован")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Ошибка блокировки слота: {e}")

    st.markdown("---")

    # Список существующих блокировок
    st.markdown("#### 📋 Текущие блокировки")
    try:
        resp = sb_read.table('blocked_slots').select('*').order('block_date').order('block_time', nullsfirst=True).execute()
        blocks = resp.data or []
    except Exception as e:
        blocks = []
        st.error(f"❌ Ошибка получения блокировок: {e}")

    # Фильтруем прошлые блокировки
    today_str = str(now_msk().date())
    blocks = [b for b in blocks if b.get('block_date') >= today_str]

    # Разделяем на блокировки дней и слотов
    day_blocks = [b for b in blocks if b.get('block_time') in (None, '')]
    time_blocks = [b for b in blocks if b.get('block_time') not in (None, '')]

    # Блокированные дни
    st.markdown("##### 📅 Заблокированные дни")
    if day_blocks:
        for b in day_blocks:
            col_d1, col_d2 = st.columns([3, 1])
            with col_d1:
                date_txt = format_date(b.get('block_date', ''))
                reason = b.get('reason')
                st.write(f"{date_txt}{' — ' + reason if reason else ''}")
            with col_d2:
                if st.button("🗑️ Удалить", key=f"del_day_{b['id']}", width='stretch'):
                    try:
                        # Сохраняем данные для Undo
                        st.session_state.last_deleted_block = b
                        (sb_write or sb_read).table('blocked_slots').delete().eq('id', b['id']).execute()
                        undo_col1, undo_col2 = st.columns([3,1])
                        with undo_col1:
                            st.success("✅ Удалено. Можно отменить действие ниже.")
                        with undo_col2:
                            if st.button("↩️ Undo", key=f"undo_day_{b['id']}", width='stretch'):
                                payload = {
                                    'block_date': b.get('block_date'),
                                    'block_time': None
                                }
                                if b.get('reason'):
                                    payload['reason'] = b.get('reason')
                                try:
                                    (sb_write or sb_read).table('blocked_slots').insert(payload).execute()
                                except Exception:
                                    (sb_write or sb_read).table('blocked_slots').insert({
                                        'block_date': b.get('block_date'),
                                        'block_time': None
                                    }).execute()
                                st.success("↩️ Восстановлено")
                                st.rerun()
                    except Exception as e:
                        st.error(f"❌ Ошибка удаления: {e}")
    else:
        st.info("Нет заблокированных дней")

    st.markdown("##### 🕐 Заблокированные слоты")
    if time_blocks:
        for b in time_blocks:
            col_t1, col_t2, col_t3 = st.columns([2, 1, 1])
            with col_t1:
                date_str = format_date(b.get('block_date', ''))
                time_str = b.get('block_time', '')
                reason = b.get('reason')
                st.write(f"{date_str} — {time_str}{' — ' + reason if reason else ''}")
            with col_t2:
                st.empty()
            with col_t3:
                if st.button("🗑️ Удалить", key=f"del_time_{b['id']}", width='stretch'):
                    try:
                        st.session_state.last_deleted_block = b
                        (sb_write or sb_read).table('blocked_slots').delete().eq('id', b['id']).execute()
                        undo_col1, undo_col2 = st.columns([3,1])
                        with undo_col1:
                            st.success("✅ Удалено. Можно отменить действие ниже.")
                        with undo_col2:
                            if st.button("↩️ Undo", key=f"undo_time_{b['id']}", width='stretch'):
                                payload = {
                                    'block_date': b.get('block_date'),
                                    'block_time': b.get('block_time')
                                }
                                if b.get('reason'):
                                    payload['reason'] = b.get('reason')
                                try:
                                    (sb_write or sb_read).table('blocked_slots').insert(payload).execute()
                                except Exception:
                                    (sb_write or sb_read).table('blocked_slots').insert({
                                        'block_date': b.get('block_date'),
                                        'block_time': b.get('block_time')
                                    }).execute()
                                st.success("↩️ Восстановлено")
                                st.rerun()
                    except Exception as e:
                        st.error(f"❌ Ошибка удаления: {e}")

def render_analytics_tab(analytics_service):
    """Вкладка аналитики"""
    st.markdown("### 📊 Аналитика")
    
    total, upcoming, this_month, this_week = analytics_service.get_stats()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 Всего", total)
    col2.metric("⏰ Предстоящих", upcoming)
    col3.metric("📅 За месяц", this_month)
    col4.metric("📆 За неделю", this_week)

    st.markdown("---")
    st.markdown("#### 🧾 Сводка по продуктам")
    from datetime import timedelta
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

def render_notifications_tab(notification_service):
    """Вкладка уведомлений"""
    st.markdown("### 🔔 Система уведомлений")
    
    # Статус бота
    st.markdown("#### 🤖 Статус Telegram бота")
    
    from config.settings import config
    if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_ADMIN_CHAT_ID:
        st.success("✅ Бот настроен и готов к работе")
        
        # Тестирование
        st.markdown("#### 🧪 Тестирование уведомлений")
        
        test_message = st.text_area("Тестовое сообщение", 
                                  "✅ Система уведомлений работает корректно!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Тест админу", use_container_width=True):
                if notification_service.bot.send_to_admin(test_message):
                    st.success("✅ Тест отправлен админу!")
                else:
                    st.error("❌ Ошибка отправки")
        
        with col2:
            test_chat_id = st.text_input("Chat ID для теста", placeholder="123456789")

def render_products_tab():
    """Управление продуктами для оплаты (первая консультация, разовая, пакеты)"""
    st.markdown("### 💳 Продукты оплаты")

    sb_read = db_manager.get_client()
    sb_write = db_manager.get_service_client()
    if sb_read is None:
        st.error("❌ Нет подключения к базе данных")
        return

    # Загрузка продуктов
    products = []
    try:
        resp = sb_read.table('products').select("*").order('sort_order').order('created_at').execute()
        products = resp.data or []
    except Exception as e:
        st.error(f"❌ Таблица products не найдена или недоступна. Ошибка: {e}")
        with st.expander("📄 Инструкция по созданию таблицы products", expanded=False):
            st.code(
                """
                CREATE TABLE IF NOT EXISTS products (
                  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                  name TEXT NOT NULL,
                  sku TEXT UNIQUE,
                  description TEXT,
                  price_rub NUMERIC(10,2) NOT NULL DEFAULT 0,
                  is_active BOOLEAN NOT NULL DEFAULT TRUE,
                  is_package BOOLEAN NOT NULL DEFAULT FALSE,
                  sessions_count INTEGER,
                  sort_order INTEGER NOT NULL DEFAULT 100,
                  is_featured BOOLEAN NOT NULL DEFAULT FALSE,
                  created_at TIMESTAMPTZ DEFAULT NOW(),
                  updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS products_active_idx ON products(is_active);
                CREATE INDEX IF NOT EXISTS products_sort_idx ON products(sort_order);
                -- Дополнительно (опционально): разрешить только один продукт со значением is_featured = TRUE
                -- Этот индекс гарантирует, что только одна строка может иметь is_featured = TRUE
                CREATE UNIQUE INDEX IF NOT EXISTS one_featured_true_idx ON products((is_featured)) WHERE is_featured;
                """,
                language="sql"
            )
        return

    # Форма создания/редактирования
    st.markdown("#### ➕ Создать/изменить продукт")
    with st.form("product_form"):
        col_a, col_b = st.columns([2, 1])
        with col_a:
            name = st.text_input("Название *", placeholder="Первая консультация")
            sku = st.text_input("SKU", placeholder="FIRST_SESSION")
            description = st.text_area("Описание", placeholder="Краткое описание продукта", height=90)
        with col_b:
            price = st.number_input("Цена, ₽", min_value=0.0, step=100.0, value=0.0, format="%0.2f")
            is_package = st.checkbox("Пакет", value=False)
            sessions = st.number_input("Кол-во сессий (для пакета)", min_value=1, step=1, value=1, disabled=not is_package)
            is_active = st.checkbox("Активен", value=True)
            sort_order = st.number_input("Порядок", min_value=1, step=1, value=100)
            is_featured = st.checkbox("Для главного экрана", value=False)

        col_save, col_cancel = st.columns([1,1])
        with col_save:
            submit = st.form_submit_button("💾 Сохранить продукт", use_container_width=True)
        with col_cancel:
            reset = st.form_submit_button("↩️ Сброс", use_container_width=True)

        if submit:
            if not name or price <= 0:
                st.error("❌ Укажите название и положительную цену")
            else:
                payload = {
                    'name': name.strip(),
                    'sku': sku.strip().upper() if sku else None,
                    'description': description.strip() if description else None,
                    'price_rub': float(price),
                    'is_active': is_active,
                    'is_package': is_package,
                    'sessions_count': int(sessions) if is_package else None,
                    'sort_order': int(sort_order),
                    'is_featured': bool(is_featured)
                }
                try:
                    # Если помечаем как featured — снимаем флаг со всех остальных
                    if payload.get('is_featured'):
                        try:
                            (sb_write or sb_read).table('products').update({'is_featured': False}).neq('id', -1).execute()
                        except Exception:
                            pass
                    (sb_write or sb_read).table('products').insert(payload).execute()
                    st.success("✅ Продукт создан")
                    st.rerun()
                except Exception as e:
                    # Попытка как upsert по SKU, если есть
                    try:
                        if payload['sku']:
                            if payload.get('is_featured'):
                                try:
                                    (sb_write or sb_read).table('products').update({'is_featured': False}).neq('sku', payload['sku']).execute()
                                except Exception:
                                    pass
                            (sb_write or sb_read).table('products').upsert(payload, on_conflict='sku').execute()
                            st.success("✅ Продукт сохранён (upsert)")
                            st.rerun()
                        else:
                            raise e
                    except Exception as e2:
                        # Повторяем без поля is_featured, если столбца ещё нет
                        try:
                            payload_fallback = dict(payload)
                            payload_fallback.pop('is_featured', None)
                            if payload_fallback.get('sku'):
                                (sb_write or sb_read).table('products').upsert(payload_fallback, on_conflict='sku').execute()
                            else:
                                (sb_write or sb_read).table('products').insert(payload_fallback).execute()
                            st.warning("⚠️ Столбец is_featured отсутствует. Добавьте его по инструкции SQL выше.")
                            st.success("✅ Продукт сохранён")
                            st.rerun()
                        except Exception as e3:
                            st.error(f"❌ Ошибка сохранения: {e3}")

    st.markdown("---")
    st.markdown("#### 📋 Список продуктов")
    if not products:
        st.info("Пока нет продуктов. Создайте первый выше.")
        return

    for p in products:
        with st.expander(f"{('🟢' if p.get('is_active') else '⚪️')} {p.get('name')} — {p.get('price_rub')} ₽", expanded=False):
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            with c1:
                st.write(f"SKU: {p.get('sku') or '—'}")
                st.write(f"Описание: {p.get('description') or '—'}")
                st.write(f"Пакет: {'Да' if p.get('is_package') else 'Нет'}")
                if p.get('is_package'):
                    st.write(f"Сессий: {p.get('sessions_count')}")
                st.write(f"Для главного экрана: {'Да' if p.get('is_featured') else 'Нет'}")
            with c2:
                new_price = st.number_input("Цена, ₽", min_value=0.0, step=100.0, value=float(p.get('price_rub') or 0), key=f"price_{p['id']}")
                new_active = st.checkbox("Активен", value=bool(p.get('is_active')), key=f"active_{p['id']}")
                new_order = st.number_input("Порядок", min_value=1, step=1, value=int(p.get('sort_order') or 100), key=f"order_{p['id']}")
            with c3:
                rename = st.text_input("Название", value=p.get('name') or '', key=f"name_{p['id']}")
                resku = st.text_input("SKU", value=p.get('sku') or '', key=f"sku_{p['id']}")
                repack = st.checkbox("Пакет", value=bool(p.get('is_package')), key=f"pkg_{p['id']}")
                recnt = st.number_input("Сессий", min_value=1, step=1, value=int(p.get('sessions_count') or 1), key=f"cnt_{p['id']}", disabled=not repack)
                new_featured = st.checkbox("Для главного экрана", value=bool(p.get('is_featured')), key=f"feat_{p['id']}")
            with c4:
                if st.button("💾 Обновить", key=f"upd_{p['id']}", use_container_width=True):
                    upd = {
                        'name': rename.strip() or p.get('name'),
                        'sku': (resku.strip().upper() if resku else None),
                        'price_rub': float(new_price),
                        'is_active': new_active,
                        'sort_order': int(new_order),
                        'is_package': repack,
                        'sessions_count': (int(recnt) if repack else None),
                        'is_featured': bool(new_featured),
                        'updated_at': now_msk().isoformat()
                    }
                    try:
                        # Если данный продукт становится featured — снимем флаг у остальных
                        if upd.get('is_featured'):
                            try:
                                sb_write.table('products').update({'is_featured': False}).neq('id', p['id']).execute()
                            except Exception:
                                pass
                        sb_write.table('products').update(upd).eq('id', p['id']).execute()
                        st.success("✅ Обновлено")
                        st.rerun()
                    except Exception as e:
                        # Повтор без is_featured, если столбец отсутствует
                        try:
                            upd_fallback = dict(upd)
                            upd_fallback.pop('is_featured', None)
                            sb_write.table('products').update(upd_fallback).eq('id', p['id']).execute()
                            st.warning("⚠️ Столбец is_featured отсутствует. Добавьте его по инструкции SQL выше.")
                            st.success("✅ Обновлено")
                            st.rerun()
                        except Exception as e2:
                            st.error(f"❌ Ошибка обновления: {e2}")
                if st.button("🗑️ Удалить", key=f"del_{p['id']}", use_container_width=True):
                    try:
                        sb_write.table('products').delete().eq('id', p['id']).execute()
                        st.success("✅ Удалено")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Ошибка удаления: {e}")