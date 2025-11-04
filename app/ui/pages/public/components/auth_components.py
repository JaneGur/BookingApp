import streamlit as st
import time
from utils.validators import validate_phone, validate_email
from core.auth import AuthManager
from services.client_service import ClientService

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

    # Если пользователь нажал "Войти сейчас" — показываем форму входа прямо здесь
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