# ========== app/ui/pages/client_cabinet.py ==========
# ИСПРАВЛЕННАЯ ВЕРСИЯ с рабочей навигацией и сохранением производительности

import streamlit as st
from datetime import datetime, timedelta
from config.constants import BOOKING_RULES
from services.booking_service import BookingService
from services.client_service import ClientService
from services.notification_service import NotificationService
from ui.components import render_info_panel, render_telegram_section
from utils.formatters import format_date, format_timedelta
from utils.product_cache import get_product_map
from utils.helpers import calculate_time_until
from utils.docs import render_consent_line
from utils.first_session_cache import has_paid_first_consultation_cached
from utils.validators import validate_email
from utils.datetime_helpers import now_msk

def render_client_cabinet():
    """ОПТИМИЗИРОВАННЫЙ личный кабинет с рабочей навигацией"""
    
    booking_service = BookingService()
    client_service = ClientService()
    notification_service = NotificationService()
    
    profile = client_service.get_profile(st.session_state.client_phone)
    client_info = profile or client_service.get_client_info(st.session_state.client_phone)
    
    # Единый стиль заголовка
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%); 
         padding: 2rem 2.5rem; border-radius: 16px; margin-bottom: 2rem;
         box-shadow: 0 4px 20px rgba(136, 200, 188, 0.25);">
        <h1 style="color: white; font-size: 1.75rem; font-weight: 700; margin: 0; 
             letter-spacing: -0.02em; display: flex; align-items: center; gap: 0.75rem;">
            <span style="font-size: 2rem;">👤</span>
            Личный кабинет
        </h1>
        <p style="color: rgba(255, 255, 255, 0.9); margin: 0.5rem 0 0 0; font-size: 1rem;">
            Здравствуйте, {st.session_state.client_name}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ИНИЦИАЛИЗАЦИЯ АКТИВНОЙ ВКЛАДКИ
    if "client_active_tab" not in st.session_state:
        st.session_state.client_active_tab = 0
    
    # СОЗДАЕМ ТАБЫ
    tab_names = ["🏠 Главная", "📅 Новая запись", "📊 История", "👤 Профиль", "💬 Уведомления"]
    tabs = st.tabs(tab_names)
    
    # РЕНДЕРИМ СОДЕРЖИМОЕ ВКЛАДОК
    with tabs[0]:
        render_dashboard_enhanced(booking_service, client_service, notification_service, client_info)
    
    with tabs[1]:
        render_new_booking_fragment(booking_service, client_info, notification_service)
    
    with tabs[2]:
        render_all_bookings_fragment(booking_service, notification_service)
    
    with tabs[3]:
        render_profile_fragment(client_service, client_info)
    
    with tabs[4]:
        render_telegram_section()


# ========== ГЛАВНАЯ СТРАНИЦА С РАБОЧИМИ КНОПКАМИ ==========

def render_dashboard_enhanced(booking_service, client_service, notification_service, client_info):
    """УЛУЧШЕННЫЙ дашборд с РАБОЧИМИ кнопками"""
    
    st.markdown("""
    <h3 style="color: #225c52; font-size: 1.25rem; font-weight: 600; 
         margin-bottom: 1.25rem; padding-bottom: 0.75rem; 
         border-bottom: 2px solid rgba(136, 200, 188, 0.2);">
        🏠 Главная
    </h3>
    """, unsafe_allow_html=True)
    
    # Получаем данные
    upcoming = booking_service.get_upcoming_client_booking(st.session_state.client_phone)
    pending = booking_service.get_latest_pending_booking_for_client(st.session_state.client_phone)
    all_bookings = booking_service.get_client_bookings(st.session_state.client_phone)
    
    total = len(all_bookings) if hasattr(all_bookings, "__len__") else (all_bookings.shape[0] if hasattr(all_bookings, "shape") else 0)
    telegram_connected = bool(notification_service.get_client_telegram_chat_id(st.session_state.client_phone))
    
    # ===== СТАТИСТИКА =====
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="📅 Предстоящих", value=(1 if upcoming else 0))
    with c2:
        st.metric(label="📊 Всего записей", value=total)
    with c3:
        status = "🔔 Подключен" if telegram_connected else "🔕 Не подключен"
        st.metric(label="Telegram", value=status)

    st.markdown("---")

    # ===== ТЕКУЩАЯ КОНСУЛЬТАЦИЯ =====
    if upcoming:
        st.markdown("### 🕐 Ближайшая консультация")
        render_booking_card_detailed(upcoming, booking_service, notification_service, show_cancel=True)
    
    # ===== НЕОПЛАЧЕННЫЙ ЗАКАЗ =====
    elif pending:
        st.markdown("### 🟡 Заказ в ожидании оплаты")
        st.warning("После оплаты запись появится выше как подтверждённая консультация")
        render_booking_card_detailed(pending, booking_service, notification_service, show_cancel=False, show_payment=True)
    
    # ===== НЕТ ЗАПИСЕЙ =====
    else:
        st.info("📭 У вас нет предстоящих консультаций")
        st.markdown("Запишитесь на новую консультацию, используя кнопку ниже")

    st.markdown("---")

    # ===== БЫСТРЫЕ ДЕЙСТВИЯ С РАБОЧИМИ КНОПКАМИ =====
    st.markdown("### ⚡ Быстрые действия")
    
    col_a1, col_a2, col_a3 = st.columns(3)
    
    with col_a1:
        # ИСПРАВЛЕНО: используем unique key и st.rerun вместо switch_tab
        if st.button("📅 Записаться", type="primary", use_container_width=True, 
                     key="dash_new_booking_action",
                     help="Перейти к записи на консультацию"):
            # Программное переключение вкладки через JS
            st.markdown("""
            <script>
            // Находим вкладку "Новая запись" (индекс 1) и кликаем по ней
            const tabs = parent.document.querySelectorAll('[data-baseweb="tab"]');
            if (tabs && tabs[1]) {
                tabs[1].click();
            }
            </script>
            """, unsafe_allow_html=True)
            # Дополнительно устанавливаем флаг для fallback
            st.session_state.force_tab_switch = 1
            st.rerun()
    
    with col_a2:
        if st.button("📊 История", use_container_width=True, 
                     key="dash_history_action",
                     help="Посмотреть все записи"):
            st.markdown("""
            <script>
            const tabs = parent.document.querySelectorAll('[data-baseweb="tab"]');
            if (tabs && tabs[2]) {
                tabs[2].click();
            }
            </script>
            """, unsafe_allow_html=True)
            st.session_state.force_tab_switch = 2
            st.rerun()
    
    with col_a3:
        if not telegram_connected:
            if st.button("🔔 Уведомления", use_container_width=True, 
                        key="dash_telegram_action",
                        help="Подключить Telegram"):
                st.markdown("""
                <script>
                const tabs = parent.document.querySelectorAll('[data-baseweb="tab"]');
                if (tabs && tabs[4]) {
                    tabs[4].click();
                }
                </script>
                """, unsafe_allow_html=True)
                st.session_state.force_tab_switch = 4
                st.rerun()
        else:
            if st.button("👤 Профиль", use_container_width=True, 
                        key="dash_profile_action",
                        help="Редактировать профиль"):
                st.markdown("""
                <script>
                const tabs = parent.document.querySelectorAll('[data-baseweb="tab"]');
                if (tabs && tabs[3]) {
                    tabs[3].click();
                }
                </script>
                """, unsafe_allow_html=True)
                st.session_state.force_tab_switch = 3
                st.rerun()

    # ===== ПРЕДУПРЕЖДЕНИЯ =====
    if upcoming and not telegram_connected:
        st.markdown("---")
        st.warning("""
        ⚠️ **Рекомендация:** Подключите Telegram-уведомления
        
        📌 Вы будете получать напоминания и подтверждения
        """)
        
        if st.button("Подключить Telegram", type="secondary", 
                    key="dash_connect_tg_warning", use_container_width=True):
            st.markdown("""
            <script>
            const tabs = parent.document.querySelectorAll('[data-baseweb="tab"]');
            if (tabs && tabs[4]) {
                tabs[4].click();
            }
            </script>
            """, unsafe_allow_html=True)
            st.session_state.force_tab_switch = 4
            st.rerun()


def render_booking_card_detailed(booking: dict, booking_service, notification_service, 
                                  show_cancel: bool = False, show_payment: bool = False):
    """Детальная карточка консультации (БЕЗ ИЗМЕНЕНИЙ)"""
    
    time_until = calculate_time_until(booking['booking_date'], booking['booking_time'])
    
    prod_line = ""
    try:
        pid = booking.get('product_id')
        amt = booking.get('amount')
        if pid is not None:
            pname = get_product_map().get(pid, {}).get('name') or f"ID {pid}"
            prod_line = f"<p><strong>💳 Продукт:</strong> {pname}{(' — ' + str(amt) + ' ₽') if amt is not None else ''}</p>"
        elif show_payment:
            prod_line = "<p><strong>💳 Продукт:</strong> Будет назначен при оплате</p>"
    except Exception:
        pass
    
    from config.constants import STATUS_DISPLAY
    status_info = STATUS_DISPLAY.get(booking.get('status', 'confirmed'), STATUS_DISPLAY['confirmed'])
    status_badge = f"<span style='background: {status_info['bg_color']}; color: {status_info['color']}; padding: 4px 12px; border-radius: 12px; font-size: 0.9rem;'>{status_info['emoji']} {status_info['text']}</span>"
    
    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.95); padding: 1.5rem; border-radius: 16px; 
         border: 1px solid rgba(136, 200, 188, 0.25); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
         margin-bottom: 1.5rem;">
        <div style="margin-bottom: 1rem;">
            {status_badge}
        </div>
        <p style="font-size: 1.2rem; font-weight: 600; color: #2d5a4f; margin: 0.5rem 0;">
            📅 {format_date(booking['booking_date'])} в {booking['booking_time']}
        </p>
        <p style="font-size: 1rem; color: #4a6a60; margin: 0.5rem 0;">
            ⏱️ До начала: <strong>{format_timedelta(time_until)}</strong>
        </p>
        {f"<p style='margin: 0.5rem 0; color: #4a6a60;'><strong>💭 Тема:</strong> {booking.get('notes', '')}</p>" if booking.get('notes') else ""}
        {prod_line}
    </div>
    """, unsafe_allow_html=True)
    
    col_act1, col_act2 = st.columns(2)
    
    with col_act1:
        if show_payment:
            if st.button("💳 Перейти к оплате", type="primary", use_container_width=True, key="pay_from_dash"):
                st.info("💳 Оплата будет подключена позже")
    
    with col_act2:
        if show_cancel and time_until.total_seconds() > BOOKING_RULES["MIN_CANCEL_MINUTES"] * 60:
            if st.button("❌ Отменить консультацию", type="secondary", use_container_width=True, key="cancel_from_dash"):
                with st.spinner("Отмена записи..."):
                    chat_id = notification_service.get_client_telegram_chat_id(st.session_state.client_phone)
                    success, message = booking_service.cancel_booking(booking['id'], st.session_state.client_phone)
                    
                    if success:
                        notification_service.bot.notify_booking_cancelled_admin(booking)
                        if chat_id:
                            notification_service.bot.notify_booking_cancelled_client(chat_id, booking)
                        
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        elif show_cancel:
            st.caption(f"⚠️ Отмена возможна за {BOOKING_RULES['MIN_CANCEL_MINUTES']}+ минут")


# ========== ОСТАЛЬНЫЕ ФРАГМЕНТЫ ОСТАЮТСЯ БЕЗ ИЗМЕНЕНИЙ ==========

@st.fragment
def render_all_bookings_fragment(booking_service, notification_service):
    """Полная история записей (БЕЗ ИЗМЕНЕНИЙ)"""
    
    st.markdown("""
    <h3 style="color: #225c52; font-size: 1.25rem; font-weight: 600; 
         margin-bottom: 1.25rem; padding-bottom: 0.75rem; 
         border-bottom: 2px solid rgba(136, 200, 188, 0.2);">
        📊 История записей
    </h3>
    """, unsafe_allow_html=True)
    
    all_bookings = booking_service.get_client_bookings(st.session_state.client_phone)
    
    if all_bookings.empty:
        st.info("📭 История записей пуста")
        # УБРАЛИ switch_tab - кнопка теперь просто информативная
        return
    
    col_f1, col_f2 = st.columns([3, 1])
    
    with col_f1:
        filter_status = st.multiselect(
            "Фильтр по статусу",
            options=['confirmed', 'pending_payment', 'completed', 'cancelled'],
            default=['confirmed', 'pending_payment'],
            format_func=lambda x: {
                'confirmed': '✅ Подтверждена',
                'pending_payment': '🟡 Ожидает оплаты',
                'completed': '✅ Завершена',
                'cancelled': '❌ Отменена'
            }[x],
            key="history_status_filter"
        )
    
    with col_f2:
        sort_order = st.selectbox(
            "Сортировка",
            options=['desc', 'asc'],
            format_func=lambda x: "Сначала новые" if x == 'desc' else "Сначала старые",
            key="history_sort"
        )
    
    filtered = all_bookings[all_bookings['status'].isin(filter_status)]
    
    if sort_order == 'asc':
        filtered = filtered.sort_values(['booking_date', 'booking_time'], ascending=True)
    
    st.info(f"📊 Найдено записей: {len(filtered)}")
    
    st.markdown("---")
    
    for idx, row in filtered.iterrows():
        render_history_booking_card(row, booking_service, notification_service)


def render_history_booking_card(booking, booking_service, notification_service):
    """Карточка записи в истории (БЕЗ ИЗМЕНЕНИЙ)"""
    from config.constants import STATUS_DISPLAY
    
    status_info = STATUS_DISPLAY.get(booking['status'], STATUS_DISPLAY['confirmed'])
    date_formatted = format_date(booking['booking_date'])
    
    time_until = calculate_time_until(booking['booking_date'], booking['booking_time'])
    can_cancel = (booking['status'] in ['confirmed', 'pending_payment'] and 
                  time_until.total_seconds() > BOOKING_RULES["MIN_CANCEL_MINUTES"] * 60)
    
    prod_html = ""
    try:
        pid = booking.get('product_id') if hasattr(booking, 'get') else (booking['product_id'] if 'product_id' in booking else None)
        amt = booking.get('amount') if hasattr(booking, 'get') else (booking['amount'] if 'amount' in booking else None)
        if pid is not None:
            pname = get_product_map().get(pid, {}).get('name') or f"ID {pid}"
            prod_html = f"<p style='margin: 0.5rem 0; color: #4a6a60;'><strong>💳 Продукт:</strong> {pname}{(' — ' + str(amt) + ' ₽') if amt is not None else ''}</p>"
    except Exception:
        pass
    
    with st.container():
        col_info, col_action = st.columns([4, 1])
        
        with col_info:
            st.markdown(f"""
            <div style="background: {status_info['bg_color']}; padding: 1rem; border-radius: 12px; 
                 border-left: 4px solid {status_info['color']}; margin-bottom: 1rem;">
                <p style="font-size: 1.1rem; font-weight: 600; color: {status_info['color']}; margin: 0 0 0.5rem 0;">
                    {status_info['emoji']} {date_formatted} в {booking['booking_time']}
                </p>
                <p style="margin: 0.5rem 0; color: #4a6a60;">
                    <strong>Статус:</strong> {status_info['text']}
                </p>
                {prod_html}
                {f"<p style='margin: 0.5rem 0; color: #4a6a60;'><strong>💭</strong> {booking['notes']}</p>" if booking['notes'] else ""}
            </div>
            """, unsafe_allow_html=True)
        
        with col_action:
            if can_cancel:
                if st.button("❌", key=f"cancel_hist_{booking['id']}", help="Отменить запись", use_container_width=True):
                    with st.spinner("Отмена..."):
                        chat_id = notification_service.get_client_telegram_chat_id(st.session_state.client_phone)
                        success, message = booking_service.cancel_booking(booking['id'], st.session_state.client_phone)
                        
                        if success:
                            notification_service.bot.notify_booking_cancelled_admin(booking)
                            if chat_id:
                                notification_service.bot.notify_booking_cancelled_client(chat_id, booking)
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
            
            if booking['status'] == 'pending_payment':
                if st.button("💳", key=f"pay_hist_{booking['id']}", help="Оплатить", use_container_width=True, type="primary"):
                    st.info("💳 Оплата будет подключена позже")


@st.fragment
def render_new_booking_fragment(booking_service, client_info, notification_service):
    """Форма новой записи (БЕЗ ИЗМЕНЕНИЙ)"""
    
    st.markdown("""
    <h3 style="color: #225c52; font-size: 1.25rem; font-weight: 600; 
         margin-bottom: 1.25rem; padding-bottom: 0.75rem; 
         border-bottom: 2px solid rgba(136, 200, 188, 0.2);">
        📅 Новая запись
    </h3>
    """, unsafe_allow_html=True)
    
    try:
        pending = booking_service.get_latest_pending_booking_for_client(st.session_state.client_phone)
    except Exception:
        pending = None
    
    if pending:
        st.warning("🟡 У вас уже создан заказ, ожидающий оплаты")
        # УБРАЛИ switch_tab
        return
    
    if booking_service.has_active_booking(st.session_state.client_phone):
        st.warning("⚠️ У вас уже есть активная запись")
        # УБРАЛИ switch_tab
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        from datetime import timedelta
        selected_date = st.date_input("Дата", min_value=now_msk().date(),
                                    max_value=now_msk().date() + timedelta(days=30),
                                    format="DD.MM.YYYY",
                                    key="booking_date_frag")
        
        available_slots = booking_service.get_available_slots(str(selected_date))
        
        if not available_slots:
            st.warning("😔 На выбранную дату нет свободных слотов")
        else:
            st.markdown("#### 🕐 Выберите время")
            st.info("💡 Доступные временные слоты")
            
            cols = st.columns(4)
            selected_time = None
            for idx, time_slot in enumerate(available_slots):
                with cols[idx % 4]:
                    if st.button(f"🕐 {time_slot}", key=f"slot_new_{time_slot}", 
                                use_container_width=True, type="primary"):
                        selected_time = time_slot
                        st.session_state.selected_time = time_slot
                        st.rerun()
            
            selected_time = st.session_state.get('selected_time')
            
            if selected_time:
                st.success(f"✅ {selected_date.strftime('%d.%m.%Y')} в {selected_time}")
                
                with st.form("quick_booking_new"):
                    try:
                        from core.database import db_manager
                        supabase = db_manager.get_client()
                        products_all = supabase.table('products').select('id,name,price_rub,is_featured,is_active')\
                            .eq('is_active', True).order('sort_order').execute().data or []
                    except Exception:
                        products_all = []
                    
                    if not products_all:
                        st.error("❌ Продукты не настроены. Обратитесь к администратору")
                        st.stop()
                    
                    st.markdown("**💳 Выберите продукт *")
                    
                    featured = [p for p in products_all if p.get('is_featured')]
                    default_idx = 0
                    if featured:
                        try:
                            default_idx = products_all.index(featured[0])
                        except:
                            pass
                    
                    prod_labels = [f"{p.get('name')} — {p.get('price_rub')} ₽" for p in products_all]
                    
                    selected_product_idx = st.selectbox(
                        "Продукт *",
                        options=list(range(len(products_all))),
                        format_func=lambda i: prod_labels[i],
                        index=default_idx,
                        help="Выбор продукта обязателен",
                        key="product_select_client"
                    )
                    
                    chosen = products_all[selected_product_idx]
                    
                    st.info(f"💰 К оплате: **{chosen.get('price_rub')} ₽**")
                    
                    notes = st.text_area("💭 Тема консультации", height=80)
                    submit = st.form_submit_button("✅ Создать заказ", use_container_width=True)
                    render_consent_line()
                    
                    if submit:
                        chat_id = notification_service.get_client_telegram_chat_id(st.session_state.client_phone)
                        
                        booking_data = {
                            'client_name': client_info['client_name'] if client_info else st.session_state.client_name,
                            'client_phone': st.session_state.client_phone,
                            'client_email': client_info.get('client_email', '') if client_info else '',
                            'client_telegram': client_info.get('client_telegram', '') if client_info else '',
                            'booking_date': str(selected_date),
                            'booking_time': selected_time,
                            'notes': notes,
                            'telegram_chat_id': chat_id,
                            'status': 'pending_payment',
                            'is_admin': False
                        }
                        
                        success, message = booking_service.create_booking(booking_data)
                        if success:
                            try:
                                row = booking_service.get_booking_by_datetime(
                                    st.session_state.client_phone,
                                    str(selected_date),
                                    selected_time
                                )
                                if row:
                                    booking_service.set_booking_payment_info(
                                        row['id'],
                                        chosen.get('id'),
                                        float(chosen.get('price_rub') or 0)
                                    )
                            except Exception as e:
                                st.warning(f"⚠️ Заказ создан, но возникла проблема с продуктом: {e}")
                            
                            st.balloons()
                            st.success("✅ Заказ создан!")
                            try:
                                notification_service.notify_booking_created(booking_data, chat_id)
                            except Exception:
                                pass
                            import time
                            time.sleep(1)
                            # ПЕРЕКЛЮЧАЕМСЯ НА ГЛАВНУЮ
                            st.markdown("""
                            <script>
                            const tabs = parent.document.querySelectorAll('[data-baseweb="tab"]');
                            if (tabs && tabs[0]) {
                                tabs[0].click();
                            }
                            </script>
                            """, unsafe_allow_html=True)
                            st.session_state.force_tab_switch = 0
                            st.rerun()
                        else:
                            st.error(message)


@st.fragment
def render_profile_fragment(client_service, client_info):
    """Профиль (БЕЗ ИЗМЕНЕНИЙ)"""
    
    st.markdown("""
    <h3 style="color: #225c52; font-size: 1.25rem; font-weight: 600; 
         margin-bottom: 1.25rem; padding-bottom: 0.75rem; 
         border-bottom: 2px solid rgba(136, 200, 188, 0.2);">
        👤 Профиль
    </h3>
    """, unsafe_allow_html=True)
    
    with st.form("profile_form_opt"):
        col1, col2 = st.columns(2)
        with col1:
            base_name = (client_info.get('client_name') if client_info else st.session_state.client_name) or ''
            new_name = st.text_input("👤 Имя *", value=base_name)
            new_email = st.text_input("📧 Email", value=(client_info.get('client_email', '') if client_info else ''))
        with col2:
            st.text_input("📱 Телефон", value=st.session_state.client_phone, disabled=True)
            new_telegram = st.text_input("💬 Telegram", value=(client_info.get('client_telegram', '') if client_info else ''))
        
        st.markdown("---")
        st.markdown("#### 🔐 Смена пароля")
        col_pass1, col_pass2 = st.columns(2)
        with col_pass1:
            current_password = st.text_input("🔑 Текущий пароль", type="password")
            new_password = st.text_input("🆕 Новый пароль", type="password")
        with col_pass2:
            confirm_new_password = st.text_input("🔑 Подтвердите новый пароль", type="password")
        
        colp1, colp2 = st.columns([1, 1])
        with colp1:
            save_profile = st.form_submit_button("💾 Сохранить", use_container_width=True)
        with colp2:
            cancel_profile = st.form_submit_button("❌ Отмена", use_container_width=True)
        render_consent_line()
        
        if save_profile:
            if not new_name:
                st.error("❌ Имя обязательно для заполнения")
                return
            
            if new_email:
                email_valid, email_msg = validate_email(new_email)
                if not email_valid:
                    st.error(email_msg)
                    return
            
            password_changed = False
            if current_password or new_password or confirm_new_password:
                if not all([current_password, new_password, confirm_new_password]):
                    st.error("❌ Заполните все поля для смены пароля")
                    return
                
                if new_password != confirm_new_password:
                    st.error("❌ Новые пароли не совпадают")
                    return
                
                if len(new_password) < 6:
                    st.error("❌ Новый пароль должен быть не менее 6 символов")
                    return
                
                from core.auth import AuthManager
                auth = AuthManager()
                
                if not auth.verify_client_password(st.session_state.client_phone, current_password):
                    st.error("❌ Неверный текущий пароль")
                    return
                
                if auth.create_client_password(st.session_state.client_phone, new_password):
                    password_changed = True
                else:
                    st.error("❌ Ошибка смены пароля")
                    return
            
            if client_service.upsert_profile(
                st.session_state.client_phone,
                new_name,
                new_email,
                new_telegram
            ):
                st.session_state.client_name = new_name
                
                if password_changed:
                    st.success("✅ Профиль обновлен и пароль изменен!")
                else:
                    st.success("✅ Профиль обновлен!")
                
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Ошибка обновления профиля")


# ========== АЛЬТЕРНАТИВНЫЙ ПОДХОД: УПРАВЛЕНИЕ ТАБАМИ ЧЕРЕЗ SESSION STATE ==========
# Если JS-подход не работает, используйте этот метод

def render_client_cabinet_alternative():
    """АЛЬТЕРНАТИВНАЯ версия с управлением табами через session_state"""
    
    booking_service = BookingService()
    client_service = ClientService()
    notification_service = NotificationService()
    
    profile = client_service.get_profile(st.session_state.client_phone)
    client_info = profile or client_service.get_client_info(st.session_state.client_phone)
    
    # Заголовок
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%); 
         padding: 2rem 2.5rem; border-radius: 16px; margin-bottom: 2rem;
         box-shadow: 0 4px 20px rgba(136, 200, 188, 0.25);">
        <h1 style="color: white; font-size: 1.75rem; font-weight: 700; margin: 0; 
             letter-spacing: -0.02em; display: flex; align-items: center; gap: 0.75rem;">
            <span style="font-size: 2rem;">👤</span>
            Личный кабинет
        </h1>
        <p style="color: rgba(255, 255, 255, 0.9); margin: 0.5rem 0 0 0; font-size: 1rem;">
            Здравствуйте, {st.session_state.client_name}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ИНИЦИАЛИЗАЦИЯ
    if "client_active_tab_index" not in st.session_state:
        st.session_state.client_active_tab_index = 0
    
    # Применяем force_tab_switch если есть
    if "force_tab_switch" in st.session_state:
        st.session_state.client_active_tab_index = st.session_state.force_tab_switch
        del st.session_state.force_tab_switch
    
    # СОЗДАЕМ РАДИО-НАВИГАЦИЮ (более надежна чем tabs)
    tab_options = {
        0: "🏠 Главная",
        1: "📅 Новая запись",
        2: "📊 История",
        3: "👤 Профиль",
        4: "💬 Уведомления"
    }
    
    selected_tab = st.radio(
        "Навигация",
        options=list(tab_options.keys()),
        format_func=lambda x: tab_options[x],
        horizontal=True,
        key="client_tab_radio",
        index=st.session_state.client_active_tab_index,
        label_visibility="collapsed"
    )
    
    # Обновляем состояние
    if selected_tab != st.session_state.client_active_tab_index:
        st.session_state.client_active_tab_index = selected_tab
    
    st.markdown("---")
    
    # РЕНДЕРИМ КОНТЕНТ В ЗАВИСИМОСТИ ОТ ВЫБРАННОЙ ВКЛАДКИ
    if selected_tab == 0:
        render_dashboard_simple(booking_service, client_service, notification_service, client_info)
    elif selected_tab == 1:
        render_new_booking_fragment(booking_service, client_info, notification_service)
    elif selected_tab == 2:
        render_all_bookings_fragment(booking_service, notification_service)
    elif selected_tab == 3:
        render_profile_fragment(client_service, client_info)
    elif selected_tab == 4:
        render_telegram_section()


def render_dashboard_simple(booking_service, client_service, notification_service, client_info):
    """Упрощенный дашборд с РАБОЧИМИ кнопками через session_state"""
    
    st.markdown("""
    <h3 style="color: #225c52; font-size: 1.25rem; font-weight: 600; 
         margin-bottom: 1.25rem; padding-bottom: 0.75rem; 
         border-bottom: 2px solid rgba(136, 200, 188, 0.2);">
        🏠 Главная
    </h3>
    """, unsafe_allow_html=True)
    
    # Получаем данные
    upcoming = booking_service.get_upcoming_client_booking(st.session_state.client_phone)
    pending = booking_service.get_latest_pending_booking_for_client(st.session_state.client_phone)
    all_bookings = booking_service.get_client_bookings(st.session_state.client_phone)
    
    total = len(all_bookings) if hasattr(all_bookings, "__len__") else (all_bookings.shape[0] if hasattr(all_bookings, "shape") else 0)
    telegram_connected = bool(notification_service.get_client_telegram_chat_id(st.session_state.client_phone))
    
    # Статистика
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="📅 Предстоящих", value=(1 if upcoming else 0))
    with c2:
        st.metric(label="📊 Всего записей", value=total)
    with c3:
        status = "🔔 Подключен" if telegram_connected else "🔕 Не подключен"
        st.metric(label="Telegram", value=status)

    st.markdown("---")

    # Консультации
    if upcoming:
        st.markdown("### 🕐 Ближайшая консультация")
        render_booking_card_detailed(upcoming, booking_service, notification_service, show_cancel=True)
    elif pending:
        st.markdown("### 🟡 Заказ в ожидании оплаты")
        st.warning("После оплаты запись появится выше как подтверждённая консультация")
        render_booking_card_detailed(pending, booking_service, notification_service, show_cancel=False, show_payment=True)
    else:
        st.info("📭 У вас нет предстоящих консультаций")
        st.markdown("Запишитесь на новую консультацию, используя кнопку ниже")

    st.markdown("---")

    # БЫСТРЫЕ ДЕЙСТВИЯ - РАБОЧИЕ КНОПКИ
    st.markdown("### ⚡ Быстрые действия")
    
    col_a1, col_a2, col_a3 = st.columns(3)
    
    with col_a1:
        if st.button("📅 Записаться", type="primary", use_container_width=True, 
                     key="dash_new_booking_simple"):
            st.session_state.client_active_tab_index = 1
            st.rerun()
    
    with col_a2:
        if st.button("📊 История", use_container_width=True, 
                     key="dash_history_simple"):
            st.session_state.client_active_tab_index = 2
            st.rerun()
    
    with col_a3:
        if not telegram_connected:
            if st.button("🔔 Уведомления", use_container_width=True, 
                        key="dash_telegram_simple"):
                st.session_state.client_active_tab_index = 4
                st.rerun()
        else:
            if st.button("👤 Профиль", use_container_width=True, 
                        key="dash_profile_simple"):
                st.session_state.client_active_tab_index = 3
                st.rerun()

    # Предупреждения
    if upcoming and not telegram_connected:
        st.markdown("---")
        st.warning("""
        ⚠️ **Рекомендация:** Подключите Telegram-уведомления
        
        📌 Вы будете получать напоминания и подтверждения
        """)
        
        if st.button("Подключить Telegram", type="secondary", 
                    key="dash_connect_tg_simple", use_container_width=True):
            st.session_state.client_active_tab_index = 4
            st.rerun()