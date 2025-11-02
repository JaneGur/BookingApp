import streamlit as st
from datetime import datetime, timedelta
from config.constants import BOOKING_RULES
from services.booking_service import BookingService
from services.client_service import ClientService
from services.notification_service import NotificationService
from ui.components import render_info_panel
from utils.validators import validate_phone, validate_email
from utils.product_cache import get_product_map
from utils.first_session_cache import has_paid_first_consultation_cached
from utils.docs import render_consent_line
from utils.datetime_helpers import now_msk

def render_public_booking():
    """Отрисовка публичной страницы записи с пошаговой формой"""
    
    # Инициализация состояния шагов
    if 'booking_step' not in st.session_state:
        st.session_state.booking_step = 1
    if 'booking_form_data' not in st.session_state:
        st.session_state.booking_form_data = {}
    
    booking_service = BookingService()
    client_service = ClientService()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_booking_steps(booking_service, client_service)
    
    with col2:
        render_info_panel()

def render_booking_steps(booking_service, client_service):
    """Отрисовка пошаговой формы"""
    current_step = st.session_state.booking_step
    
    # Индикатор прогресса
    render_progress_indicator(current_step)
    
    st.markdown("---")
    
    # Отрисовка текущего шага
    if current_step == 1:
        render_step_datetime(booking_service)
    elif current_step == 2:
        render_step_user_data()
    elif current_step == 3:
        render_step_confirmation(booking_service)
    elif current_step == 4:
        render_step_authorization(booking_service, client_service)

def render_progress_indicator(current_step):
    """Визуальный индикатор прогресса"""
    steps = [
        {"num": 1, "icon": "📅", "title": "Дата и время"},
        {"num": 2, "icon": "👤", "title": "Ваши данные"},
        {"num": 3, "icon": "✅", "title": "Подтверждение"},
        {"num": 4, "icon": "🔐", "title": "Авторизация"}
    ]
    
    cols = st.columns(4)
    
    for idx, step in enumerate(steps):
        with cols[idx]:
            if step["num"] < current_step:
                # Завершенный шаг
                st.markdown(f"""
                <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%); 
                     border-radius: 12px; color: white; box-shadow: 0 2px 8px rgba(136, 200, 188, 0.3);">
                    <div style="font-size: 28px; margin-bottom: 5px;">✓</div>
                    <div style="font-size: 12px; font-weight: 600;">{step["title"]}</div>
                </div>
                """, unsafe_allow_html=True)
            elif step["num"] == current_step:
                # Текущий шаг
                st.markdown(f"""
                <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%); 
                     border-radius: 12px; color: white; box-shadow: 0 4px 12px rgba(136, 200, 188, 0.4);
                     border: 3px solid rgba(255, 255, 255, 0.5);">
                    <div style="font-size: 28px; margin-bottom: 5px;">{step["icon"]}</div>
                    <div style="font-size: 12px; font-weight: 700;">{step["title"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Будущий шаг
                st.markdown(f"""
                <div style="text-align: center; padding: 15px; background: rgba(240, 242, 245, 0.5); 
                     border-radius: 12px; color: #9ca3af; border: 2px dashed rgba(156, 163, 175, 0.3);">
                    <div style="font-size: 28px; margin-bottom: 5px; opacity: 0.5;">{step["icon"]}</div>
                    <div style="font-size: 12px; font-weight: 500;">{step["title"]}</div>
                </div>
                """, unsafe_allow_html=True)

def render_step_datetime(booking_service):
    """Шаг 1: Выбор даты и времени"""
    st.markdown("### 📅 Шаг 1: Выберите дату и время")
    st.caption("Всё время — по Москве (MSK)")
    
    # Выбор даты
    min_date = now_msk().date()
    max_date = min_date + timedelta(days=BOOKING_RULES["MAX_DAYS_AHEAD"])
    
    selected_date = st.date_input(
        "Дата консультации", 
        min_value=min_date,
        max_value=max_date, 
        value=st.session_state.booking_form_data.get('date', min_date),
        format="DD.MM.YYYY",
        key="step1_date"
    )
    
    # Получаем доступные слоты
    available_slots = booking_service.get_available_slots(str(selected_date))
    
    if not available_slots:
        st.warning("😔 На выбранную дату нет свободных слотов. Выберите другую дату.")
        return
    
    st.markdown("#### 🕐 Доступные временные слоты")
    st.info(f"💡 Доступно {len(available_slots)} слотов на {selected_date.strftime('%d.%m.%Y')}")
    
    # Отображение слотов в сетке
    cols = st.columns(4)
    selected_time = st.session_state.booking_form_data.get('time')
    
    for idx, time_slot in enumerate(available_slots):
        with cols[idx % 4]:
            is_selected = (time_slot == selected_time)
            button_type = "primary" if is_selected else "secondary"
            label = f"{'✓ ' if is_selected else ''}🕐 {time_slot}"
            
            if st.button(label, key=f"slot_{time_slot}", use_container_width=True, type=button_type):
                st.session_state.booking_form_data['date'] = selected_date
                st.session_state.booking_form_data['time'] = time_slot
                st.rerun()
    
    # Кнопки навигации
    st.markdown("---")
    col_nav1, col_nav2 = st.columns([1, 1])
    
    with col_nav2:
        if selected_time:
            if st.button("Далее ➡️", use_container_width=True, type="primary"):
                st.session_state.booking_step = 2
                st.rerun()
        else:
            st.button("Выберите время", use_container_width=True, disabled=True)

def render_step_user_data():
    """Шаг 2: Заполнение данных пользователя"""
    st.markdown("### 👤 Шаг 2: Ваши данные")
    
    form_data = st.session_state.booking_form_data
    
    # Показываем выбранные дату и время
    if form_data.get('date') and form_data.get('time'):
        st.success(f"✅ Выбрано: **{form_data['date'].strftime('%d.%m.%Y')}** в **{form_data['time']}**")
    
    st.markdown("---")
    
    # Форма данных
    col_a, col_b = st.columns(2)
    
    with col_a:
        client_name = st.text_input(
            "👤 Ваше имя *", 
            placeholder="Иван Иванов",
            value=form_data.get('name', ''),
            key="step2_name"
        )
        
        client_email = st.text_input(
            "📧 Email", 
            placeholder="example@mail.com",
            value=form_data.get('email', ''),
            key="step2_email"
        )
        
        client_chat_id = st.text_input(
            "💬 ID Telegram для уведомлений", 
            placeholder="123456789 (опционально)",
            value=form_data.get('chat_id', ''),
            help="Чтобы получать уведомления о записи и напоминания",
            key="step2_chat"
        )
    
    with col_b:
        client_phone = st.text_input(
            "📱 Телефон *", 
            placeholder="+7 (999) 123-45-67",
            value=form_data.get('phone', ''),
            key="step2_phone"
        )
        
        client_telegram = st.text_input(
            "💬 Telegram username", 
            placeholder="@username",
            value=form_data.get('telegram', ''),
            key="step2_telegram"
        )
    
    notes = st.text_area(
        "💭 Тема консультации (необязательно)", 
        height=80,
        value=form_data.get('notes', ''),
        placeholder="Опишите, что вас беспокоит или какой вопрос хотите обсудить...",
        key="step2_notes"
    )
    
    # Кнопки навигации
    st.markdown("---")
    col_nav1, col_nav2 = st.columns([1, 1])
    
    with col_nav1:
        if st.button("⬅️ Назад", use_container_width=True):
            st.session_state.booking_step = 1
            st.rerun()
    
    with col_nav2:
        if st.button("Далее ➡️", use_container_width=True, type="primary"):
            # Обрезаем случайные пробелы у вводимых полей (не трогаем пароли)
            client_name_clean = client_name.strip() if isinstance(client_name, str) else client_name
            client_phone_clean = client_phone.strip() if isinstance(client_phone, str) else client_phone
            client_email_clean = client_email.strip() if isinstance(client_email, str) else client_email
            client_telegram_clean = client_telegram.strip() if isinstance(client_telegram, str) else client_telegram
            client_chat_id_clean = client_chat_id.strip() if isinstance(client_chat_id, str) else client_chat_id
            notes_clean = notes.strip() if isinstance(notes, str) else notes

            # Валидация
            if not client_name_clean or not client_phone_clean:
                st.error("❌ Заполните имя и телефон")
            else:
                phone_valid, phone_msg = validate_phone(client_phone_clean)
                if not phone_valid:
                    st.error(phone_msg)
                else:
                    if client_email_clean:
                        email_valid, email_msg = validate_email(client_email_clean)
                        if not email_valid:
                            st.error(email_msg)
                            return

                    # Сохраняем данные
                    st.session_state.booking_form_data.update({
                        'name': client_name_clean,
                        'phone': client_phone_clean,
                        'email': client_email_clean,
                        'telegram': client_telegram_clean,
                        'chat_id': client_chat_id_clean,
                        'notes': notes_clean
                    })

                    st.session_state.booking_step = 3
                    st.rerun()

def render_step_confirmation(booking_service):
    """Шаг 3: Подтверждение заказа"""
    st.markdown("### ✅ Шаг 3: Подтверждение заказа")
    
    form_data = st.session_state.booking_form_data
    
    # Получаем продукт по умолчанию
    try:
        from core.database import db_manager
        supabase = db_manager.get_client()
        products_all = supabase.table('products').select('id,name,price_rub,is_featured,is_active').eq('is_active', True).order('sort_order').execute().data or []
    except Exception:
        products_all = []
    
    featured = [p for p in products_all if p.get('is_featured')]
    chosen = (featured[0] if featured else (products_all[0] if products_all else None))
    
    # Карточка подтверждения
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.95); padding: 25px; border-radius: 16px; 
         border: 1px solid rgba(136, 200, 188, 0.25); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);">
    """, unsafe_allow_html=True)
    
    st.markdown("#### 📋 Детали записи")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📅 Дата и время:**")
        st.info(f"🗓️ {form_data.get('date').strftime('%d.%m.%Y')}\n\n🕐 {form_data.get('time')}")
        
        st.markdown("**👤 Ваши данные:**")
        st.write(f"**Имя:** {form_data.get('name')}")
        st.write(f"**Телефон:** {form_data.get('phone')}")
        if form_data.get('email'):
            st.write(f"**Email:** {form_data.get('email')}")
        if form_data.get('telegram'):
            st.write(f"**Telegram:** {form_data.get('telegram')}")
    
    with col2:
        if chosen:
            st.markdown("**💳 Продукт:**")
            st.success(f"""
            **{chosen.get('name')}**
            
            💰 Стоимость: **{chosen.get('price_rub')} ₽**
            """)
        
        if form_data.get('notes'):
            st.markdown("**💭 Тема консультации:**")
            st.info(form_data.get('notes'))
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Согласие с условиями
    st.markdown("---")
    render_consent_line()
    
    # Кнопки навигации
    st.markdown("---")
    col_nav1, col_nav2 = st.columns([1, 1])
    
    with col_nav1:
        if st.button("⬅️ Назад", use_container_width=True):
            st.session_state.booking_step = 2
            st.rerun()
    
    with col_nav2:
        if st.button("✅ Создать заказ", use_container_width=True, type="primary"):
            # Создаем заказ
            booking_data = {
                'client_name': form_data.get('name'),
                'client_phone': form_data.get('phone'),
                'client_email': form_data.get('email', ''),
                'client_telegram': form_data.get('telegram', ''),
                'booking_date': str(form_data.get('date')),
                'booking_time': form_data.get('time'),
                'notes': form_data.get('notes', ''),
                'telegram_chat_id': form_data.get('chat_id', ''),
                'status': 'pending_payment'
            }
            
            success, message = booking_service.create_booking(booking_data)
            
            if success:
                # Сохраняем контекст для следующего шага
                st.session_state.booking_form_data['booking_created'] = True
                
                # Автоназначаем продукт
                if chosen:
                    try:
                        row = booking_service.get_booking_by_datetime(
                            form_data.get('phone'),
                            str(form_data.get('date')),
                            form_data.get('time')
                        )
                        if row:
                            booking_service.set_booking_payment_info(
                                row['id'], 
                                chosen.get('id'), 
                                float(chosen.get('price_rub') or 0)
                            )
                            st.session_state.booking_form_data['booking_id'] = row['id']
                    except Exception:
                        pass
                
                st.balloons()
                st.success("✅ Заказ успешно создан!")
                st.session_state.booking_step = 4
                st.rerun()
            else:
                st.error(message)

def render_step_authorization(booking_service, client_service):
    """Шаг 4: Авторизация и переход в личный кабинет"""
    st.markdown("### 🔐 Шаг 4: Авторизация")
    
    form_data = st.session_state.booking_form_data
    
    # Показываем успешное создание заказа
    st.success("🎉 Ваш заказ успешно создан!")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(255, 243, 224, 0.95) 0%, rgba(255, 224, 178, 0.95) 100%); 
         padding: 20px; border-radius: 12px; border-left: 4px solid #ff9800; margin: 20px 0;">
        <h4 style="margin: 0 0 10px 0; color: #e65100;">⏳ Заказ ожидает оплаты</h4>
        <p style="margin: 0; color: #5d4037;">
            Для завершения записи войдите в личный кабинет и перейдите к оплате.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### Выберите действие:")
    
    tab1, tab2, tab3 = st.tabs(["🔐 Войти", "📝 Регистрация", "💳 Оплатить позже"])
    
    with tab1:
        render_login_tab(form_data, client_service)
    
    with tab2:
        render_registration_tab(form_data, client_service)
    
    with tab3:
        render_pay_later_tab(form_data)

def render_login_tab(form_data, client_service):
    """Вкладка входа"""
    st.markdown("##### Войдите в существующий аккаунт")
    
    with st.form("step4_login"):
        login_phone = st.text_input(
            "📱 Номер телефона", 
            placeholder="+7 (999) 123-45-67",
            value=form_data.get('phone', '')
        )
        login_password = st.text_input("🔑 Пароль", type="password")
        
        submitted = st.form_submit_button("🔐 Войти и перейти к оплате", use_container_width=True)
        
        if submitted:
            if not login_phone or not login_password:
                st.error("❌ Заполните все поля")
            else:
                # Обрезаем пробелы у номера
                login_phone_clean = login_phone.strip() if isinstance(login_phone, str) else login_phone
                from core.auth import AuthManager
                auth_manager = AuthManager()
                
                if auth_manager.verify_client_password(login_phone_clean, login_password):
                    # Получаем информацию о клиенте
                    profile = client_service.get_profile(login_phone_clean)
                    client_info = profile or client_service.get_client_info(login_phone_clean)
                    
                    if client_info:
                        # Авторизуем
                        st.session_state.client_logged_in = True
                        st.session_state.client_phone = login_phone_clean
                        st.session_state.client_name = client_info['client_name']
                        st.session_state.client_nav = "👁️ Мои ближайшие консультации"
                        
                        # Remember me token
                        try:
                            token = auth_manager.issue_remember_token(login_phone_clean)
                            if token:
                                st.query_params["rt"] = token
                        except Exception:
                            pass
                        
                        # Очищаем форму
                        st.session_state.booking_step = 1
                        st.session_state.booking_form_data = {}
                        
                        st.success("✅ Вход выполнен! Перенаправляем в личный кабинет...")
                        st.rerun()
                    else:
                        st.error("❌ Клиент не найден")
                else:
                    st.error("❌ Неверный номер телефона или пароль")

def render_registration_tab(form_data, client_service):
    """Вкладка регистрации"""
    st.markdown("##### Создайте новый аккаунт")
    st.info("💡 Регистрация позволит управлять записями и получать уведомления")
    
    with st.form("step4_registration"):
        reg_name = st.text_input("👤 Имя", value=form_data.get('name', ''))
        reg_phone = st.text_input("📱 Телефон", value=form_data.get('phone', ''))
        reg_email = st.text_input("📧 Email", value=form_data.get('email', ''))
        
        col_pass1, col_pass2 = st.columns(2)
        with col_pass1:
            reg_password = st.text_input("🔑 Придумайте пароль", type="password", help="Минимум 6 символов")
        with col_pass2:
            reg_confirm = st.text_input("🔑 Подтвердите пароль", type="password")
        
        submitted = st.form_submit_button("📝 Зарегистрироваться и перейти к оплате", use_container_width=True)
        
        if submitted:
            # Обрезаем пробелы у полей (кроме пароля)
            reg_name_clean = reg_name.strip() if isinstance(reg_name, str) else reg_name
            reg_phone_clean = reg_phone.strip() if isinstance(reg_phone, str) else reg_phone
            reg_email_clean = reg_email.strip() if isinstance(reg_email, str) else reg_email

            if not reg_name_clean or not reg_phone_clean or not reg_password:
                st.error("❌ Заполните все обязательные поля")
            elif reg_password != reg_confirm:
                st.error("❌ Пароли не совпадают")
            elif len(reg_password) < 6:
                st.error("❌ Пароль должен быть не менее 6 символов")
            else:
                from core.auth import AuthManager
                from utils.validators import validate_phone, validate_email
                
                phone_valid, phone_msg = validate_phone(reg_phone_clean)
                if not phone_valid:
                    st.error(phone_msg)
                    return
                
                if reg_email_clean:
                    email_valid, email_msg = validate_email(reg_email_clean)
                    if not email_valid:
                        st.error(email_msg)
                        return
                
                auth_manager = AuthManager()
                
                # Создаем аккаунт
                if auth_manager.create_client_password(reg_phone_clean, reg_password):
                    # Сохраняем профиль
                    try:
                        client_service.upsert_profile(
                            reg_phone_clean, 
                            reg_name_clean, 
                            reg_email_clean, 
                            form_data.get('telegram', '').strip()
                        )
                    except Exception:
                        pass
                    
                    # Авторизуем
                    st.session_state.client_logged_in = True
                    st.session_state.client_phone = reg_phone_clean
                    st.session_state.client_name = reg_name_clean
                    st.session_state.client_nav = "👁️ Мои ближайшие консультации"
                    
                    # Remember me token
                    try:
                        token = auth_manager.issue_remember_token(reg_phone_clean)
                        if token:
                            st.query_params["rt"] = token
                    except Exception:
                        pass
                    
                    # Очищаем форму
                    st.session_state.booking_step = 1
                    st.session_state.booking_form_data = {}
                    
                    st.success("✅ Регистрация завершена! Перенаправляем в личный кабинет...")
                    st.rerun()
                else:
                    st.error("❌ Ошибка регистрации")

def render_pay_later_tab(form_data):
    """Вкладка отложенной оплаты"""
    st.markdown("##### Оплатить позже")
    
    st.warning("""
    ⚠️ **Важно:** Без авторизации вы не сможете управлять заказом
    
    Ваш заказ создан, но для доступа к нему и оплаты необходимо войти в личный кабинет.
    """)
    
    st.info("""
    📌 **Что делать дальше:**
    1. Вернитесь на главную страницу
    2. Войдите в личный кабинет через кнопку "🔐 Войти в кабинет" внизу страницы
    3. Найдите ваш заказ в разделе "Мои ближайшие консультации"
    4. Оплатите заказ
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🏠 На главную", use_container_width=True, type="primary"):
            # Сбрасываем форму
            st.session_state.booking_step = 1
            st.session_state.booking_form_data = {}
            st.rerun()
    
    with col2:
        if st.button("🔐 Войти сейчас", use_container_width=True):
            st.session_state.show_client_login = True
            st.rerun()