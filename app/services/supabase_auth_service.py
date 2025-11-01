from typing import Optional
from urllib.parse import urljoin
import streamlit as st
from core.database import db_manager
from config.settings import config


class SupabaseAuthService:
    def __init__(self):
        self.client = db_manager.get_client()

    def sign_up(self, email: str, password: str, redirect_to: Optional[str] = None):
        if not self.client:
            return None
        try:
            payload = {"email": email, "password": password}
            redir = redirect_to or config.APP_BASE_URL
            if redir:
                payload["options"] = {"email_redirect_to": redir}
            return self.client.auth.sign_up(payload)
        except Exception as e:
            st.error(f"❌ Ошибка регистрации: {e}")
            return None

    def sign_in(self, email: str, password: str):
        if not self.client:
            return None
        try:
            return self.client.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
        except Exception as e:
            st.error(f"❌ Ошибка входа: {e}")
            return None

    def reset_password_for_email(self, email: str, redirect_to: Optional[str] = None):
        if not self.client:
            return None
        try:
            redir = redirect_to or config.APP_BASE_URL
            opts = {"redirect_to": redir} if redir else {}
            return self.client.auth.reset_password_for_email(email, opts)
        except Exception as e:
            st.error(f"❌ Ошибка сброса пароля: {e}")
            return None

    def set_session_from_redirect(self, access_token: str, refresh_token: Optional[str] = None):
        if not self.client:
            return None
        try:
            return self.client.auth.set_session({
                "access_token": access_token,
                "refresh_token": refresh_token or "",
            })
        except Exception as e:
            st.error(f"❌ Ошибка установки сессии: {e}")
            return None

    def update_password(self, new_password: str):
        if not self.client:
            return None
        try:
            return self.client.auth.update_user({
                "password": new_password,
            })
        except Exception as e:
            st.error(f"❌ Ошибка обновления пароля: {e}")
            return None

    def get_user(self):
        if not self.client:
            return None
        try:
            return self.client.auth.get_user()
        except Exception as e:
            return None

    def sign_out(self):
        if not self.client:
            return None
        try:
            return self.client.auth.sign_out()
        except Exception:
            return None
