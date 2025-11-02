import streamlit as st
import time
from core.auth import AuthManager
from services.client_service import ClientService
from services.booking_service import BookingService
from utils.validators import validate_phone, validate_email
from services.notification_service import NotificationService
from utils.docs import render_consent_line

def render_auth_forms():
    """Отрисовка форм аутентификации"""
    auth_manager = AuthManager()
    client_service = ClientService()
    booking_service = BookingService()
    
    # Форма входа в личный кабинет
    if st.session_state.show_client_login:
        render_login_form(auth_manager, client_service)
    
    # Форма регистрации
    elif st.session_state.show_client_registration:
        render_registration_form(auth_manager, client_service)
    
    # Форма сброса пароля
    elif st.session_state.show_password_reset:
        render_password_reset_form(auth_manager)

def render_login_form(auth_manager, client_service):
    """Оптимизированная форма входа - минимум запросов к БД"""
    st.markdown("### 🔐 Вход в личный кабинет")
    
    with st.form("client_login_form", clear_on_submit=False):
        login_phone = st.text_input("📱 Номер телефона", placeholder="+7 (999) 123-45-67")
        login_password = st.text_input("🔑 Пароль", type="password", placeholder="Введите ваш пароль")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            login_submit = st.form_submit_button("Войти", width='stretch', type="primary")
        with col2:
            if st.form_submit_button("❌ Отмена", width='stretch'):
                st.session_state.show_client_login = False
                st.rerun()
        
        if login_submit:
            if not login_phone or not login_password:
                st.error("❌ Заполните номер телефона и пароль")
            else:
                # Обрезаем случайные пробелы у номера
                login_phone_clean = login_phone.strip() if isinstance(login_phone, str) else login_phone
                # Показываем spinner только на время проверки
                with st.spinner("🔐 Проверка..."):
                    if auth_manager.verify_client_password(login_phone_clean, login_password):
                        # Параллельно получаем информацию (одним запросом)
                        profile = client_service.get_profile(login_phone_clean)
                        
                        if profile:
                            # Быстрая авторизация
                            st.session_state.client_logged_in = True
                            st.session_state.client_phone = login_phone_clean
                            st.session_state.client_name = profile['client_name']
                            st.session_state.show_client_login = False
                            
                            # Remember token (быстро, не блокирует UI)
                            try:
                                token = auth_manager.issue_remember_token(login_phone_clean)
                                if token:
                                    st.query_params["rt"] = token
                            except:
                                pass
                            
                            st.success("✅ Успешный вход!")
                            # Минимальная задержка для читаемости
                            time.sleep(0.3)
                            st.rerun()
                        else:
                            st.error("❌ Клиент не найден")
                    else:
                        st.error("❌ Неверный номер телефона или пароль")
def render_registration_form(auth_manager, client_service):
    """Форма регистрации"""
    st.markdown("### 📝 Регистрация в личном кабинете")
    st.info("""
    **Зачем регистрироваться?**
    • 🔒 Безопасный доступ к вашим записям
    • 📋 Просмотр истории консультаций  
    • 🔔 Получение уведомлений
    • ⏰ Управление предстоящими записями
    """)
    
    with st.form("client_registration_form"):
        st.markdown("#### 👤 Основная информация")
        client_name = st.text_input("👤 Ваше имя *", placeholder="Иван Иванов", 
                                  value=st.session_state.get('registration_name', ''))
        client_phone = st.text_input("📱 Номер телефона *", placeholder="+7 (999) 123-45-67",
                                   value=st.session_state.get('registration_phone', ''))
        client_email = st.text_input("📧 Email (необязательно)", placeholder="example@mail.com")
        
        st.markdown("#### 🔐 Безопасность")
        password = st.text_input("🔑 Пароль *", type="password", 
                               help="Пароль должен быть не менее 6 символов")
        confirm_password = st.text_input("🔑 Подтвердите пароль *", type="password")
        
        st.markdown("#### 💬 Дополнительно")
        client_telegram = st.text_input("💬 Telegram (необязательно)", placeholder="@username")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            register_submit = st.form_submit_button("📝 Зарегистрироваться", width='stretch')
        with col2:
            if st.form_submit_button("❌ Отмена", width='stretch'):
                st.session_state.show_client_registration = False
                st.rerun()
        
        if register_submit:
            # Обрезаем пробелы у вводимых полей (кроме пароля)
            client_name_clean = client_name.strip() if isinstance(client_name, str) else client_name
            client_phone_clean = client_phone.strip() if isinstance(client_phone, str) else client_phone
            client_email_clean = client_email.strip() if isinstance(client_email, str) else client_email
            client_telegram_clean = client_telegram.strip() if isinstance(client_telegram, str) else client_telegram

            # Валидация
            if not client_name_clean or not client_phone_clean or not password:
                st.error("❌ Заполните все обязательные поля")
            elif password != confirm_password:
                st.error("❌ Пароли не совпадают")
            elif len(password) < 6:
                st.error("❌ Пароль должен быть не менее 6 символов")
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

                    # Создаем учетную запись
                    if auth_manager.create_client_password(client_phone_clean, password):
                        st.success("✅ Учетная запись создана!")
                        
                        # Автоматически логиним пользователя
                        if auth_manager.verify_client_password(client_phone_clean, password):
                            # Сохраняем профиль клиента
                            try:
                                client_service.upsert_profile(client_phone_clean, client_name_clean, client_email_clean or '', client_telegram_clean or '')
                            except Exception:
                                pass
                            client_info = client_service.get_profile(client_phone_clean) or client_service.get_client_info(client_phone_clean)
                            # Логинимся даже если информации о клиенте ещё нет в БД
                            st.session_state.client_logged_in = True
                            st.session_state.client_phone = client_phone_clean
                            st.session_state.client_name = (client_info['client_name'] if client_info else client_name_clean)
                            st.session_state.show_client_registration = False
                            # Remember me token -> query param
                            try:
                                token = auth_manager.issue_remember_token(client_phone_clean)
                                if token:
                                    st.query_params["rt"] = token
                            except Exception:
                                pass
                            st.rerun()
                    else:
                        st.error("❌ Ошибка создания учетной записи")
    render_consent_line()
    
    st.markdown("---")
    if st.button("🔐 Уже есть аккаунт? Войдите"):
        st.session_state.show_client_registration = False
        st.session_state.show_client_login = True
        st.rerun()

def render_password_reset_form(auth_manager):
    """Форма сброса пароля"""
    st.markdown("### 🔑 Восстановление пароля")
    
    with st.form("password_reset_form"):
        reset_phone = st.text_input("📱 Номер телефона", placeholder="+7 (999) 123-45-67")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            reset_submit = st.form_submit_button("🔑 Сбросить пароль", width='stretch')
        with col2:
            if st.form_submit_button("❌ Отмена", width='stretch'):
                st.session_state.show_password_reset = False
                st.rerun()
        
        if reset_submit:
            if not reset_phone:
                st.error("❌ Введите номер телефона")
            else:
                reset_phone_clean = reset_phone.strip() if isinstance(reset_phone, str) else reset_phone
                phone_valid, phone_msg = validate_phone(reset_phone_clean)
                if not phone_valid:
                    st.error(phone_msg)
                else:
                    # Генерируем временный пароль
                    temp_password = auth_manager.generate_temporary_password()
                    
                    # Сохраняем новый пароль
                    if auth_manager.send_password_reset(reset_phone_clean, temp_password):
                        # Пытаемся отправить через Telegram
                        notif = NotificationService()
                        chat_id = notif.get_client_telegram_chat_id(reset_phone)
                        if chat_id:
                            sent = notif.bot.send_to_client(chat_id, f"🔑 Ваш временный пароль: <b>{temp_password}</b>\nПожалуйста, смените его после входа.")
                            if sent:
                                st.success("✅ Временный пароль отправлен в Telegram")
                                st.info("ℹ️ Проверьте чат с ботом")
                            else:
                                st.warning("⚠️ Не удалось отправить в Telegram. Пароль показан ниже:")
                                st.success(f"🔑 Временный пароль: **{temp_password}**")
                        else:
                            # Фоллбек: показываем пароль на экране
                            st.success(f"🔑 Временный пароль: **{temp_password}**")
                            st.info("⚠️ Сохраните его и смените после входа!")
                    else:
                        st.error("❌ Ошибка сброса пароля")
    render_consent_line()
    
    st.markdown("---")
    if st.button("🔐 Войти в аккаунт"):
        st.session_state.show_password_reset = False
        st.session_state.show_client_login = True
        st.rerun()