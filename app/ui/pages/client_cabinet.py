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
    """Отрисовка личного кабинета клиента"""
    st.title("👤 Личный кабинет")
    
    booking_service = BookingService()
    client_service = ClientService()
    notification_service = NotificationService()
    
    # Профиль: сначала пробуем из client_profiles, иначе из последней записи
    profile = client_service.get_profile(st.session_state.client_phone)
    client_info = profile or client_service.get_client_info(st.session_state.client_phone)
    
    st.markdown(f"""
    <div class=\"welcome-header\">
        <h1>👋 Здравствуйте, {st.session_state.client_name}!</h1>
        <p>Добро пожаловать в личный кабинет</p>
    </div>
    """, unsafe_allow_html=True)

    # ===== Навигация (радио на стейте) =====
    sections = [
        "🏠 Главная", "📅 Записаться на консультацию", "👁️ Мои ближайшие консультации",
        "📊 История консультаций", "👤 Профиль", "💬 Уведомления"
    ]

    # Синхронизация с существующим sidebar (реагируем только на изменение выбора в нём)
    sidebar_to_top = {
        "👁️ Мои ближайшие консультации": "👁️ Мои ближайшие консультации",
        "👤 Профиль": "👤 Профиль",
        "💬 Уведомления": "💬 Уведомления",
        "📅 Записаться на консультацию": "📅 Записаться на консультацию",
        "📊 История записей": "📊 История",
    }
    top_to_sidebar = {
        "👁️ Мои ближайшие консультации": "👁️ Мои ближайшие консультации",
        "👤 Профиль": "👤 Профиль",
        "💬 Уведомления": "💬 Уведомления",
        "📅 Записаться на консультацию": "📅 Записаться на консультацию",
        "📊 История": "📊 История записей",
        "🏠 Главная": None,
    }

    sidebar_selected = st.session_state.get("client_tabs")
    prev_sidebar_selected = st.session_state.get("_sidebar_prev")
    # Если пришли из публичной страницы с флагом — один раз фиксируем Главную и не даём сайдбару перезаписать
    if st.session_state.get('client_go_home_once'):
        st.session_state.client_nav = "🏠 Главная"
        st.session_state._sidebar_prev = sidebar_selected
        st.session_state.client_go_home_once = False
    elif sidebar_selected != prev_sidebar_selected:
        st.session_state._sidebar_prev = sidebar_selected
        if sidebar_selected in sidebar_to_top:
            st.session_state.client_nav = sidebar_to_top[sidebar_selected]
            st.rerun()

    if "client_nav" not in st.session_state:
        st.session_state.client_nav = "🏠 Главная"

    # Верхняя навигация
    nav_col = st.container()
    with nav_col:
        selected = st.radio("Навигация", sections, index=sections.index(st.session_state.client_nav), horizontal=True)
        if selected != st.session_state.client_nav:
            st.session_state.client_nav = selected
            # Обновляем sidebar, чтобы он соответствовал верхней навигации
            mapped = top_to_sidebar.get(selected)
            if mapped:
                st.session_state.current_tab = mapped
            st.rerun()

    # Роутер секций
    route = st.session_state.client_nav
    if route == "🏠 Главная":
        # Одноразовый баннер после создания заказа из публичной страницы
        try:
            ctx = st.session_state.get('client_pending_created_ctx')
            if ctx:
                st.success("✅ Заказ создан и ожидает оплаты. Найдите его ниже или перейдите в 'Мои ближайшие консультации'.")
                st.session_state.client_pending_created_ctx = None
        except Exception:
            pass
        render_dashboard(booking_service, client_service, notification_service, client_info)
    elif route == "📅 Записаться на консультацию":
        render_new_booking_section(booking_service, client_info, notification_service)
    elif route == "👁️ Мои ближайшие консультации":
        render_current_booking(booking_service, notification_service)
    elif route == "📊 История консультаций":
        render_booking_history(booking_service)
    elif route == "👤 Профиль":
        render_profile_section(client_service, client_info)
    elif route == "💬 Уведомления":
        render_telegram_section()

def render_dashboard(booking_service, client_service, notification_service, client_info):
    upcoming = booking_service.get_upcoming_client_booking(st.session_state.client_phone)
    all_bookings = booking_service.get_client_bookings(st.session_state.client_phone)
    total = len(all_bookings) if hasattr(all_bookings, "__len__") else (all_bookings.shape[0] if hasattr(all_bookings, "shape") else 0)
    telegram_connected = bool(notification_service.get_client_telegram_chat_id(st.session_state.client_phone))
    pending_exists = booking_service.get_latest_pending_booking_for_client(st.session_state.client_phone) is not None

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="Предстоящие", value=(1 if upcoming else 0))
    with c2:
        st.metric(label="Всего записей", value=total)
    with c3:
        st.metric(label="Telegram", value=("Подключен" if telegram_connected else "Не подключен"))

    st.markdown("#### Быстрые действия")
    ac1, ac2, ac3 = st.columns(3)
    with ac1:
        if st.button("📅 Записаться на консультацию", type="primary", width='stretch'):
            st.session_state.client_nav = "📅 Записаться на консультацию"
            st.rerun()
    with ac2:
        if not telegram_connected:
            if st.button("🔔 Подключить Telegram", width='stretch'):
                st.session_state.client_nav = "💬 Уведомления"
                st.rerun()
        else:
            if st.button("👁️ Мои ближайшие консультации", width='stretch'):
                st.session_state.client_nav = "👁️ Мои ближайшие консультации"
                st.rerun()
    with ac3:
        if st.button("👤 Профиль", width='stretch'):
            st.session_state.client_nav = "👤 Профиль"
            st.rerun()

    # Заголовок с бейджем при наличии неоплаченного заказа
    badge = " <span style='background:#FFE08A;color:#614a00;border-radius:999px;padding:2px 8px;font-size:12px;'>Новый неоплаченный заказ</span>" if pending_exists and not upcoming else ""
    st.markdown(f"#### Ближайшая запись{badge}", unsafe_allow_html=True)
    if upcoming:
        time_until = calculate_time_until(upcoming['booking_date'], upcoming['booking_time'])
        prod_line = ""
        try:
            pid = upcoming.get('product_id')
            amt = upcoming.get('amount')
            if pid is not None:
                pname = get_product_map().get(pid, {}).get('name') or f"ID {pid}"
                prod_line = f"<p><strong>💳 Продукт:</strong> {pname}{(' — ' + str(amt) + ' ₽') if amt is not None else ''}</p>"
        except Exception:
            pass
        st.markdown(f"""
        <div class=\"booking-card\">
            <h3>🕐 Ближайшая консультация</h3>
            <p><strong>📅 Дата:</strong> {format_date(upcoming['booking_date'])}</p>
            <p><strong>🕐 Время:</strong> {upcoming['booking_time']}</p>
            <p><strong>⏱️ До начала:</strong> {format_timedelta(time_until)}</p>
            {f"<p><strong>💭 Комментарий:</strong> {upcoming['notes']}</p>" if upcoming['notes'] else ""}
            {prod_line}
        </div>
        """, unsafe_allow_html=True)
    else:
        # Нет подтверждённых — проверим заказы в ожидании оплаты
        pending = booking_service.get_latest_pending_booking_for_client(st.session_state.client_phone)
        if pending:
            st.warning("🟡 У вас есть неоплаченный заказ. После оплаты запись появится здесь.")
            with st.container():
                prod_line = "<p><strong>💳 Продукт:</strong> Не выбран</p>"
                try:
                    pid = pending.get('product_id')
                    amt = pending.get('amount')
                    if pid is not None:
                        pname = get_product_map().get(pid, {}).get('name') or f"ID {pid}"
                        prod_line = f"<p><strong>💳 Продукт:</strong> {pname}{(' — ' + str(amt) + ' ₽') if amt is not None else ''}</p>"
                except Exception:
                    pass
                st.markdown(f"""
                <div class=\"booking-card\">
                    <h4>🟡 Заказ в ожидании оплаты</h4>
                    <p><strong>📅 Дата:</strong> {format_date(pending['booking_date'])}</p>
                    <p><strong>🕐 Время:</strong> {pending['booking_time']}</p>
                    {prod_line}
                </div>
                """, unsafe_allow_html=True)
                try:
                    from core.database import db_manager
                    supabase = db_manager.get_client()
                    products_all = supabase.table('products').select('*').eq('is_active', True).order('sort_order').execute().data or []
                except Exception:
                    products_all = []

                has_paid_first = has_paid_first_consultation_cached(st.session_state.client_phone)
                def is_first_product(p):
                    sku = (p.get('sku') or '').upper()
                    name = (p.get('name') or '').lower()
                    return sku == 'FIRST_SESSION' or ('перва' in name and 'консультац' in name)
                filtered = [p for p in (products_all or []) if not (has_paid_first and is_first_product(p))]
                featured = [p for p in filtered if p.get('is_featured')]
                chosen = (featured[0] if featured else (filtered[0] if filtered else None))

                # Применяем к заказу, если ещё не применено
                try:
                    row = pending
                    if row and chosen and not row.get('product_id'):
                        booking_service.set_booking_payment_info(row['id'], chosen.get('id'), float(chosen.get('price_rub') or 0))
                except Exception:
                    pass

                # Показываем назначенный продукт
                try:
                    row = pending
                    pid = row.get('product_id')
                    amt = row.get('amount')
                    pmap = get_product_map()
                    pname = pmap.get(pid, {}).get('name') if pid is not None else None
                    pname_disp = pname or (f"ID {pid}" if pid is not None else '—')
                    st.success(f"🧾 Продукт для заказа: {pname_disp}{f' — {amt} ₽' if amt is not None else ''}")
                except Exception:
                    pass

                if st.button("Перейти к оплате", type="primary", width='stretch', key="btn_go_pay_pending"):
                    st.info("Оплата будет подключена позже. Сейчас это заглушка.")
        else:
            st.info("📭 Нет предстоящих консультаций")

def render_current_booking(booking_service, notification_service):
    """Отрисовка текущей записи"""
    st.markdown("### 👁️ Текущая запись")
    
    upcoming = booking_service.get_upcoming_client_booking(st.session_state.client_phone)
    
    if upcoming:
        time_until = calculate_time_until(upcoming['booking_date'], upcoming['booking_time'])
        # Получаем название продукта, если выбран
        prod_line = ""
        try:
            pid = upcoming.get('product_id')
            amt = upcoming.get('amount')
            if pid is not None:
                from core.database import db_manager
                supabase = db_manager.get_client()
                presp = supabase.table('products').select('name').eq('id', pid).limit(1).execute()
                pname = presp.data[0]['name'] if presp.data else f"ID {pid}"
                prod_line = f"<p><strong>💳 Продукт:</strong> {pname}{(' — ' + str(amt) + ' ₽') if amt is not None else ''}</p>"
        except Exception:
            pass
        st.markdown(f"""
        <div class="booking-card">
            <h3>🕐 Ближайшая консультация</h3>
            <p><strong>📅 Дата:</strong> {format_date(upcoming['booking_date'])}</p>
            <p><strong>🕐 Время:</strong> {upcoming['booking_time']}</p>
            <p><strong>⏱️ До начала:</strong> {format_timedelta(time_until)}</p>
            {f"<p><strong>💭 Комментарий:</strong> {upcoming['notes']}</p>" if upcoming['notes'] else ""}
            {prod_line}
        </div>
        """, unsafe_allow_html=True)

        # Если это заказ в ожидании оплаты — автоназначаем продукт (без выбора)
        if str(upcoming.get('status')) == 'pending_payment':
            try:
                from core.database import db_manager
                supabase = db_manager.get_client()
                products_all = supabase.table('products').select('*').eq('is_active', True).order('sort_order').execute().data or []
            except Exception:
                products_all = []

            has_paid_first = has_paid_first_consultation_cached(st.session_state.client_phone)
            def is_first_product(p):
                sku = (p.get('sku') or '').upper()
                name = (p.get('name') or '').lower()
                return sku == 'FIRST_SESSION' or ('перва' in name and 'консультац' in name)
            filtered = [p for p in (products_all or []) if not (has_paid_first and is_first_product(p))]
            featured = [p for p in filtered if p.get('is_featured')]
            chosen = (featured[0] if featured else (filtered[0] if filtered else None))

            try:
                if chosen and not upcoming.get('product_id'):
                    booking_service.set_booking_payment_info(upcoming['id'], chosen.get('id'), float(chosen.get('price_rub') or 0))
            except Exception:
                pass

            if st.button("Перейти к оплате", type="primary", width='stretch', key="btn_go_pay_current"):
                st.info("Оплата будет подключена позже. Сейчас это заглушка.")
        
        # Проверяем подключен ли Telegram
        telegram_connected = notification_service.get_client_telegram_chat_id(st.session_state.client_phone)
        if not telegram_connected:
            st.warning("""
            ⚠️ **Вы не получаете напоминания!**
            
            Подключите Telegram в разделе "💬 Уведомления" чтобы получать:
            • ⏰ Напоминание за 1 час до консультации
            • ✅ Подтверждения новых записей
            • ❌ Уведомления об отменах
            """)
        
        if time_until.total_seconds() > BOOKING_RULES["MIN_CANCEL_MINUTES"] * 60:
            if st.button("❌ Отменить запись", type="secondary", width='stretch'):
                # Получаем chat_id для уведомления
                chat_id = notification_service.get_client_telegram_chat_id(st.session_state.client_phone)
                success, message = booking_service.cancel_booking(upcoming['id'], st.session_state.client_phone)
                if success:
                    # Отправляем уведомления об отмене
                    notification_service.bot.notify_booking_cancelled_admin(upcoming)
                    if chat_id:
                        notification_service.bot.notify_booking_cancelled_client(chat_id, upcoming)
                    
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.warning(f"⚠️ Отмена возможна за {BOOKING_RULES['MIN_CANCEL_MINUTES']}+ минут")
    else:
        st.info("📭 Нет предстоящих консультаций")

def render_profile_section(client_service, client_info):
    """Отрисовка раздела профиля"""
    st.markdown("### 👤 Профиль")
    
    # Показываем форму всегда, даже если информации ещё нет
    with st.form("profile_form"):
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
            new_password = st.text_input("🆕 Новый пароль", type="password", 
                                       help="Пароль должен быть не менее 6 символов")
        with col_pass2:
            confirm_new_password = st.text_input("🔑 Подтвердите новый пароль", type="password")
        
        colp1, colp2 = st.columns([1, 1])
        with colp1:
            save_profile = st.form_submit_button("💾 Сохранить", use_container_width=True)
        with colp2:
            cancel_profile = st.form_submit_button("❌ Отмена", use_container_width=True)
        render_consent_line()
        
        if save_profile:
            changes_made = False
            messages = []
            
            # Валидация email
            if new_email:
                email_valid, email_msg = validate_email(new_email)
                if not email_valid:
                    st.error(email_msg)
                    return
            # Сохраняем профиль в client_profiles (мягко, если таблицы нет)
            saved = client_service.upsert_profile(
                st.session_state.client_phone,
                new_name.strip(),
                new_email.strip(),
                new_telegram.strip(),
            )
            if saved:
                messages.append("✅ Профиль сохранён")
                changes_made = True

            # Проверяем смену пароля
            if current_password or new_password or confirm_new_password:
                from core.auth import AuthManager
                auth_manager = AuthManager()
                
                if not current_password:
                    st.error("❌ Введите текущий пароль для смены")
                elif not auth_manager.verify_client_password(st.session_state.client_phone, current_password):
                    st.error("❌ Неверный текущий пароль")
                elif new_password != confirm_new_password:
                    st.error("❌ Новые пароли не совпадают")
                elif len(new_password) < 6:
                    st.error("❌ Новый пароль должен быть не менее 6 символов")
                else:
                    if auth_manager.create_client_password(st.session_state.client_phone, new_password):
                        messages.append("✅ Пароль успешно изменен!")
                        changes_made = True
                    else:
                        st.error("❌ Ошибка при смене пароля")
            
            if changes_made:
                for msg in messages:
                    st.success(msg)
                st.rerun()

def render_new_booking_section(booking_service, client_info, notification_service):
    """Отрисовка раздела новой записи"""
    st.markdown("### 📅 Записаться на консультацию")

    # Если есть неоплаченный заказ — показать баннер и ссылку перейти к оплате
    try:
        pending = booking_service.get_latest_pending_booking_for_client(st.session_state.client_phone)
    except Exception:
        pending = None
    if pending:
        st.warning("🟡 У вас уже создан новый заказ и он ожидает оплаты.")
        col_goto, _ = st.columns([1,3])
        with col_goto:
            if st.button("Перейти к оплате", type="primary", use_container_width=True, key="go_to_pay_from_new_booking"):
                st.session_state.client_nav = "👁️ Мои ближайшие консультации"
                st.rerun()
    
    if booking_service.has_active_booking(st.session_state.client_phone):
        st.warning("⚠️ У вас уже есть активная запись. Перейдите в 'Мои ближайшие консультации'.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            from datetime import timedelta
            selected_date = st.date_input("Дата", min_value=now_msk().date(),
                                        max_value=now_msk().date() + timedelta(days=30),
                                        format="DD.MM.YYYY")
            available_slots = booking_service.get_available_slots(str(selected_date))
            
            # Адаптация рендеринга слотов
            if not available_slots:
                st.warning("😔 На выбранную дату нет свободных слотов")
            else:
                st.markdown("#### 🕐 Выберите время")
                st.info("💡 Доступные для записи временные слотов")
                
                cols = st.columns(4)
                selected_time = None
                for idx, time_slot in enumerate(available_slots):
                    with cols[idx % 4]:
                        if st.button(f"🕐 {time_slot}", key=f"client_slot_{time_slot}", 
                                    use_container_width=True, type="primary"):
                            selected_time = time_slot
                            st.session_state.selected_time = time_slot
                            st.rerun()
                
                selected_time = st.session_state.get('selected_time')
                
                if selected_time:
                    st.success(f"✅ {selected_date.strftime('%d.%m.%Y')} в {selected_time}")
                    
                    with st.form("quick_booking"):
                        # Плашка с продуктом по умолчанию (только в форме заказа)
                        try:
                            from core.database import db_manager
                            supabase = db_manager.get_client()
                            products_all = supabase.table('products').select('id,name,price_rub,is_featured,is_active').eq('is_active', True).order('sort_order').execute().data or []
                        except Exception:
                            products_all = []
                        featured = [p for p in products_all if p.get('is_featured')]
                        chosen = (featured[0] if featured else (products_all[0] if products_all else None))
                        if chosen:
                            st.success(f"💳 Будет оформлен продукт: {chosen.get('name')} — {chosen.get('price_rub')} ₽")
                        notes = st.text_area("💭 Тема консультации", height=80)
                        submit = st.form_submit_button("✅ Создать заказ", use_container_width=True)
                        render_consent_line()
                        
                        if submit:
                            # Получаем chat_id для уведомления
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
                                'status': 'pending_payment'
                            }
                            
                            success, message = booking_service.create_booking(booking_data)
                            if success:
                                st.balloons()
                                st.info("🟡 Заказ создан и ожидает оплаты. После оплаты он появится в разделе 'Текущая запись'.")
                                # Отправляем уведомление (как заказ) и показываем секцию оплаты после rerun
                                try:
                                    notification_service.notify_booking_created(booking_data, chat_id)
                                except Exception:
                                    pass
                                # Сохраняем контекст для секции оплаты и перерисовываем
                                st.session_state._pending_payment_ctx = {
                                    'date': str(selected_date),
                                    'time': selected_time
                                }
                                st.rerun()
                            else:
                                st.error(message)
                    
                    # Секция оплаты вне формы — если есть созданный заказ
                    ctx = st.session_state.get('_pending_payment_ctx')
                    if ctx and ctx.get('date') == str(selected_date) and ctx.get('time') == selected_time:
                        st.markdown("---")
                        st.markdown("#### 💳 Оплата заказа")
                        try:
                            from core.database import db_manager
                            supabase = db_manager.get_client()
                            products_all = supabase.table('products').select('*').eq('is_active', True).order('sort_order').execute().data
                        except Exception:
                            products_all = []
                        # Фильтрация "первой консультации" если уже была оплачена (кэш)
                        has_paid_first = has_paid_first_consultation_cached(st.session_state.client_phone)
                        def is_first_product(p):
                            sku = (p.get('sku') or '').upper()
                            name = (p.get('name') or '').lower()
                            return sku == 'FIRST_SESSION' or ('перва' in name and 'консультац' in name)
                        products = [p for p in (products_all or []) if not (has_paid_first and is_first_product(p))]
                        featured = [p for p in products if p.get('is_featured')]
                        chosen = (featured[0] if featured else (products[0] if products else None))

                        # Присваиваем выбранный продукт
                        booking_row = booking_service.get_booking_by_datetime(
                            st.session_state.client_phone, ctx['date'], ctx['time']
                        )
                        if booking_row and chosen:
                            try:
                                booking_service.set_booking_payment_info(booking_row['id'], chosen.get('id'), float(chosen.get('price_rub') or 0))
                            except Exception:
                                pass
                        # Показываем выбранный
                        if booking_row:
                            pid = booking_row.get('product_id')
                            amt = booking_row.get('amount')
                            pmap = get_product_map()
                            pname = pmap.get(pid, {}).get('name') if pid is not None else None
                            pname_disp = pname or (f"ID {pid}" if pid is not None else '—')
                            st.info(f"🧾 Продукт для заказа: {pname_disp}{f' — {amt} ₽' if amt is not None else ''}")
                        col_pay1, col_pay2 = st.columns([1,1])
                        with col_pay1:
                            if st.button("Перейти к оплате", type="primary", width='stretch'):
                                st.info("Оплата будет подключена позже. Сейчас это заглушка.")
                        with col_pay2:
                            if st.button("Оплатить позже", width='stretch'):
                                st.session_state.client_nav = "🏠 Главная"
                                st.session_state._pending_payment_ctx = None
                                st.rerun()
        
        with col2:
            render_info_panel()

def render_booking_history(booking_service):
    """Отрисовка истории записей"""
    st.markdown("### 📊 История записей")
    
    bookings = booking_service.get_client_bookings(st.session_state.client_phone)
    
    if not bookings.empty:
        for idx, row in bookings.iterrows():
            from config.constants import STATUS_DISPLAY
            status_info = STATUS_DISPLAY.get(row['status'], STATUS_DISPLAY['confirmed'])
            date_formatted = format_date(row['booking_date'])
            # Строка продукта по записи
            prod_html = ""
            try:
                pid = row.get('product_id') if hasattr(row, 'get') else (row['product_id'] if 'product_id' in row else None)
                amt = row.get('amount') if hasattr(row, 'get') else (row['amount'] if 'amount' in row else None)
                if pid is not None:
                    pname = get_product_map().get(pid, {}).get('name') or f"ID {pid}"
                    prod_html = f"<p><strong>💳 Продукт:</strong> {pname}{(' — ' + str(amt) + ' ₽') if amt is not None else ''}</p>"
                else:
                    prod_html = "<p><strong>💳 Продукт:</strong> Не выбран</p>"
            except Exception:
                pass
            st.markdown(f"""
            <div class="booking-card">
                <h4>{status_info['emoji']} {date_formatted} в {row['booking_time']}</h4>
                <p><strong>Статус:</strong> <span style="color: {status_info['color']}">{status_info['text']}</span></p>
                {prod_html}
                {f"<p><strong>💭</strong> {row['notes']}</p>" if row['notes'] else ""}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📭 История пуста")