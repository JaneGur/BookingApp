import streamlit as st
import time
from utils.validators import validate_phone, validate_email
from core.auth import AuthManager
from services.client_service import ClientService
from services.notification_service import NotificationService

def render_login_tab(form_data, client_service):
    """Вкладка входа с возможностью сброса пароля"""
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
                login_phone_clean = login_phone.strip() if isinstance(login_phone, str) else login_phone
                auth_manager = AuthManager()
                
                if auth_manager.verify_client_password(login_phone_clean, login_password):
                    profile = client_service.get_profile(login_phone_clean)
                    client_info = profile or client_service.get_client_info(login_phone_clean)
                    
                    if client_info:
                        st.session_state.client_logged_in = True
                        st.session_state.client_phone = login_phone_clean
                        st.session_state.client_name = client_info['client_name']
                        st.session_state.client_nav = "👁️ Мои ближайшие консультации"
                        
                        try:
                            token = auth_manager.issue_remember_token(login_phone_clean)
                            if token:
                                st.query_params["rt"] = token
                        except Exception:
                            pass
                        
                        st.session_state.booking_step = 1
                        st.session_state.booking_form_data = {}
                        
                        st.success("✅ Вход выполнен! Перенаправляем в личный кабинет...")
                        st.rerun()
                    else:
                        st.error("❌ Клиент не найден")
                else:
                    st.error("❌ Неверный номер телефона или пароль")
    
    # ДОБАВЛЕНА ССЫЛКА НА СБРОС ПАРОЛЯ
    st.markdown("---")
    st.markdown("##### 🔑 Забыли пароль?")
    
    if st.button("Сбросить пароль", use_container_width=True, key="forgot_password_link"):
        st.session_state.show_password_reset_public = True
        st.rerun()
    
    # ФОРМА СБРОСА ПАРОЛЯ (если активирована)
    if st.session_state.get('show_password_reset_public'):
        render_password_reset_form_public()


def render_password_reset_form_public():
    """Форма сброса пароля на публичной странице"""
    st.markdown("---")
    st.markdown("### 🔑 Восстановление пароля")
    
    st.info("""
    💡 **Как это работает:**
    - Если у вас подключен Telegram, новый пароль будет отправлен туда
    - Если Telegram не подключен, пароль отобразится на экране
    """)
    
    with st.form("public_password_reset_form"):
        reset_phone = st.text_input(
            "📱 Номер телефона",
            placeholder="+7 (999) 123-45-67",
            help="Введите номер телефона, который вы использовали при регистрации"
        )
        
        col_submit, col_cancel = st.columns([1, 1])
        
        with col_submit:
            reset_submit = st.form_submit_button("🔑 Сбросить пароль", use_container_width=True, type="primary")
        
        with col_cancel:
            cancel_submit = st.form_submit_button("❌ Отмена", use_container_width=True)
        
        if cancel_submit:
            st.session_state.show_password_reset_public = False
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
                    with st.spinner("🔄 Проверяем данные..."):
                        time.sleep(0.3)
                        
                        # Проверяем, существует ли клиент
                        auth_manager = AuthManager()
                        client_service = ClientService()
                        
                        # Проверяем наличие пароля
                        if not auth_manager.client_has_password(reset_phone_clean):
                            st.error("❌ Учетная запись с таким номером не найдена или не имеет пароля")
                            st.info("💡 Возможно, вы еще не регистрировались. Попробуйте создать аккаунт.")
                        else:
                            # Генерируем новый пароль
                            temp_password = auth_manager.generate_temporary_password()
                            
                            with st.spinner("🔐 Генерируем новый пароль..."):
                                time.sleep(0.2)
                                
                                if auth_manager.send_password_reset(reset_phone_clean, temp_password):
                                    # Пытаемся отправить в Telegram
                                    notification_service = NotificationService()
                                    chat_id = notification_service.get_client_telegram_chat_id(reset_phone_clean)
                                    
                                    telegram_sent = False
                                    
                                    if chat_id:
                                        with st.spinner("📤 Отправляем пароль в Telegram..."):
                                            time.sleep(0.2)
                                            
                                            message = f"""
🔑 <b>Восстановление пароля</b>

Ваш новый временный пароль:
<code>{temp_password}</code>

⚠️ <b>Важно:</b>
• Используйте этот пароль для входа
• Рекомендуем сменить пароль в личном кабинете
• Никому не сообщайте свой пароль

Если вы не запрашивали восстановление пароля, проигнорируйте это сообщение.
                                            """
                                            
                                            telegram_sent = notification_service.bot.send_to_client(chat_id, message)
                                    
                                    # Показываем результат
                                    if telegram_sent:
                                        st.balloons()
                                        st.success("✅ Новый пароль отправлен в Telegram!")
                                        st.info("📱 Проверьте чат с ботом для получения пароля")
                                        
                                        # Кнопка закрытия
                                        if st.button("✅ Понятно, закрыть", use_container_width=True, key="close_after_telegram"):
                                            st.session_state.show_password_reset_public = False
                                            st.rerun()
                                    else:
                                        # Telegram не подключен или отправка не удалась
                                        st.warning("⚠️ Не удалось отправить пароль в Telegram")
                                        st.info("💡 Ваш новый пароль показан ниже. Сохраните его!")
                                        
                                        # Показываем пароль на экране
                                        st.markdown("""
                                        <div style="background: linear-gradient(135deg, rgba(255, 243, 224, 0.95) 0%, rgba(255, 224, 178, 0.95) 100%); 
                                             padding: 20px; border-radius: 12px; border-left: 4px solid #ff9800; margin: 20px 0;">
                                            <h4 style="margin: 0 0 10px 0; color: #e65100;">🔑 Ваш новый пароль</h4>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        # Отображаем пароль с возможностью копирования
                                        st.code(temp_password, language=None)
                                        
                                        st.warning("""
                                        ⚠️ **Важные рекомендации:**
                                        - Скопируйте пароль прямо сейчас
                                        - Используйте его для входа
                                        - Смените пароль в личном кабинете после входа
                                        - Никому не сообщайте свой пароль
                                        """)
                                        
                                        # Кнопки действий
                                        col_act1, col_act2 = st.columns(2)
                                        
                                        with col_act1:
                                            if st.button("🔐 Войти с новым паролем", use_container_width=True, type="primary", key="login_after_reset"):
                                                st.session_state.show_password_reset_public = False
                                                st.rerun()
                                        
                                        with col_act2:
                                            if st.button("❌ Закрыть", use_container_width=True, key="close_after_screen"):
                                                st.session_state.show_password_reset_public = False
                                                st.rerun()
                                else:
                                    st.error("❌ Ошибка сброса пароля. Попробуйте позже или обратитесь к администратору")


def render_registration_tab(form_data, client_service):
    """Вкладка регистрации (без изменений)"""
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
                auth_manager = AuthManager()
                
                phone_valid, phone_msg = validate_phone(reg_phone_clean)
                if not phone_valid:
                    st.error(phone_msg)
                    return
                
                if reg_email_clean:
                    email_valid, email_msg = validate_email(reg_email_clean)
                    if not email_valid:
                        st.error(email_msg)
                        return
                
                if auth_manager.create_client_password(reg_phone_clean, reg_password):
                    try:
                        client_service.upsert_profile(
                            reg_phone_clean, 
                            reg_name_clean, 
                            reg_email_clean, 
                            form_data.get('telegram', '').strip()
                        )
                    except Exception:
                        pass
                    
                    st.session_state.client_logged_in = True
                    st.session_state.client_phone = reg_phone_clean
                    st.session_state.client_name = reg_name_clean
                    st.session_state.client_nav = "👁️ Мои ближайшие консультации"
                    
                    try:
                        token = auth_manager.issue_remember_token(reg_phone_clean)
                        if token:
                            st.query_params["rt"] = token
                    except Exception:
                        pass
                    
                    st.session_state.booking_step = 1
                    st.session_state.booking_form_data = {}
                    
                    st.success("✅ Регистрация завершена! Перенаправляем в личный кабинет...")
                    st.rerun()
                else:
                    st.error("❌ Ошибка регистрации")


def render_pay_later_tab(form_data):
    """Вкладка отложенной оплаты (без изменений)"""
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
            with st.spinner("⏳ Возврат на главную..."):
                time.sleep(0.2)
                st.session_state.booking_step = 1
                st.session_state.booking_form_data = {}
                st.rerun()
    
    with col2:
        if st.button("🔐 Войти сейчас", use_container_width=True):
            with st.spinner("⏳ Открываем форму входа..."):
                time.sleep(0.2)
                st.session_state.show_client_login = True
                st.rerun()

    if st.session_state.get("show_client_login"):
        st.markdown("---")
        st.markdown("#### Вход в личный кабинет")
        with st.form("pay_later_login_form"):
            login_phone = st.text_input(
                "📱 Номер телефона",
                placeholder="+7 (999) 123-45-67",
                key="pay_later_login_phone"
            )
            login_password = st.text_input("🔑 Пароль", type="password", key="pay_later_login_password")
            submitted = st.form_submit_button("🔐 Войти", use_container_width=True)
            if submitted:
                if not login_phone or not login_password:
                    st.error("❌ Заполните все поля")
                else:
                    login_phone_clean = login_phone.strip() if isinstance(login_phone, str) else login_phone
                    auth_manager = AuthManager()
                    if auth_manager.verify_client_password(login_phone_clean, login_password):
                        client_service = ClientService()
                        profile = client_service.get_profile(login_phone_clean)
                        client_info = profile or client_service.get_client_info(login_phone_clean)
                        if client_info:
                            st.session_state.client_logged_in = True
                            st.session_state.client_phone = login_phone_clean
                            st.session_state.client_name = client_info['client_name']
                            st.session_state.client_nav = "👁️ Мои ближайшие консультации"
                            try:
                                token = auth_manager.issue_remember_token(login_phone_clean)
                                if token:
                                    st.query_params["rt"] = token
                            except Exception:
                                pass
                            st.success("✅ Вход выполнен! Перенаправляем...")
                            st.session_state.show_client_login = False
                            st.rerun()
                        else:
                            st.error("❌ Не удалось найти профиль клиента")
                    else:
                        st.error("❌ Неверный номер телефона или пароль")