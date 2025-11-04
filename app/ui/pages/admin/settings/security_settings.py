import streamlit as st
from core.auth import AuthManager
from services.notification_service import NotificationService
from utils.datetime_helpers import now_msk

def render_security_settings():
    """Настройки безопасности"""
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