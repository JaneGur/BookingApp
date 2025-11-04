import streamlit as st
import time
from utils.validators import validate_phone, validate_email
from ..utils.scroll_helpers import render_step_anchor, render_field_anchor, render_navigation_anchor

def render_step_user_data():
    """Шаг 2: Заполнение данных с якорями для каждого поля"""
    render_step_anchor("step2-form")
    st.markdown("### 👤 Шаг 2: Ваши данные")
    
    form_data = st.session_state.booking_form_data
    
    # Показываем выбранные дату и время
    if form_data.get('date') and form_data.get('time'):
        st.success(f"✅ Выбрано: **{form_data['date'].strftime('%d.%m.%Y')}** в **{form_data['time']}**")
    
    st.markdown("---")
    
    # Форма данных с якорями для мобильной прокрутки
    col_a, col_b = st.columns(2)
    
    with col_a:
        render_field_anchor("name")
        client_name = st.text_input(
            "👤 Ваше имя *", 
            placeholder="Иван Иванов",
            value=form_data.get('name', ''),
            key="step2_name"
        )
        
        render_field_anchor("email")
        client_email = st.text_input(
            "📧 Email", 
            placeholder="example@mail.com",
            value=form_data.get('email', ''),
            key="step2_email"
        )
        
        st.info("Если хотите получать уведомления в Telegram, подключите бота позже в личном кабинете в разделе 'Уведомления'")
    
    with col_b:
        render_field_anchor("phone")
        client_phone = st.text_input(
            "📱 Телефон *",
            placeholder="+7XXXXXXXXXX",
            value=form_data.get('phone', ''),
            key="step2_phone"
        )
        render_field_anchor("telegram")
        client_telegram = st.text_input(
            "💬 Telegram username",
            placeholder="@username",
            value=form_data.get('telegram', ''),
            key="step2_telegram"
        )
    
    render_field_anchor("notes")
    notes = st.text_area(
        "💭 Тема консультации (необязательно)", 
        height=80,
        value=form_data.get('notes', ''),
        placeholder="Опишите, что вас беспокоит или какой вопрос хотите обсудить...",
        key="step2_notes"
    )
    
    # Кнопки навигации
    st.markdown("---")
    render_navigation_anchor(2)
    col_nav1, col_nav2 = st.columns([1, 1])
    
    with col_nav1:
        if st.button("⬅️ Назад", use_container_width=True, key="step2_back"):
            with st.spinner("Пожалуйста, подождите..."):
                time.sleep(0.2)
                st.session_state.booking_step = 1
                st.rerun()
    
    with col_nav2:
        if st.button("Далее ➡️", use_container_width=True, type="primary", key="step2_next"):
            with st.spinner("Пожалуйста, подождите..."):
                time.sleep(0.2)
                # Валидация и переход
                client_name_clean = client_name.strip() if isinstance(client_name, str) else client_name
                client_phone_clean = client_phone.strip() if isinstance(client_phone, str) else client_phone
                client_email_clean = client_email.strip() if isinstance(client_email, str) else client_email
                client_telegram_clean = client_telegram.strip() if isinstance(client_telegram, str) else client_telegram
                notes_clean = notes.strip() if isinstance(notes, str) else notes
                
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
                        
                        st.session_state.booking_form_data.update({
                            'name': client_name_clean,
                            'phone': client_phone_clean,
                            'email': client_email_clean,
                            'telegram': client_telegram_clean,
                            'notes': notes_clean
                        })
                        st.session_state.booking_step = 3
                        st.rerun()