import hashlib
import secrets
import streamlit as st
from datetime import datetime, timedelta
from core.database import db_manager
from config.settings import config
from utils.validators import normalize_phone, hash_password, hash_password_secure, verify_password
from utils.datetime_helpers import now_msk
import hmac
import json
import base64

class AuthManager:
    def __init__(self):
        self.supabase = db_manager.get_client()
    
    def hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_client_password(self, phone: str, password: str) -> bool:
        """Создание пароля для клиента"""
        try:
            phone_hash = hash_password(normalize_phone(phone))
            password_hash = hash_password_secure(password)
            
            response = self.supabase.table('client_auth').upsert({
                'phone_hash': phone_hash,
                'password_hash': password_hash,
                'created_at': now_msk().isoformat()
            }).execute()
            
            return bool(response.data)
        except Exception as e:
            st.error(f"❌ Ошибка создания пароля: {e}")
            return False
    
    def verify_client_password(self, phone: str, password: str) -> bool:
        """Проверка пароля клиента"""
        try:
            phone_hash = hash_password(normalize_phone(phone))
            
            response = self.supabase.table('client_auth')\
                .select('password_hash')\
                .eq('phone_hash', phone_hash)\
                .execute()
            
            if response.data:
                stored_hash = response.data[0]['password_hash']
                if verify_password(password, stored_hash):
                    return True
            return False
        except Exception as e:
            st.error(f"❌ Ошибка проверки пароля: {e}")
            return False
    
    def client_has_password(self, phone: str) -> bool:
        """Проверка наличия пароля у клиента"""
        try:
            phone_hash = hash_password(normalize_phone(phone))
            
            response = self.supabase.table('client_auth')\
                .select('password_hash')\
                .eq('phone_hash', phone_hash)\
                .execute()
            
            return bool(response.data and response.data[0]['password_hash'])
        except Exception as e:
            return False
    
    def send_password_reset(self, phone: str, new_password: str) -> bool:
        """Сброс пароля клиента"""
        try:
            phone_hash = hash_password(normalize_phone(phone))
            password_hash = hash_password_secure(new_password)
            
            response = self.supabase.table('client_auth').upsert({
                'phone_hash': phone_hash,
                'password_hash': password_hash,
                'updated_at': now_msk().isoformat()
            }).execute()
            
            return bool(response.data)
        except Exception as e:
            st.error(f"❌ Ошибка сброса пароля: {e}")
            return False
    
    def generate_temporary_password(self) -> str:
        """Генерация временного пароля"""
        return secrets.token_urlsafe(8)
    
    def check_admin_password(self, password: str) -> bool:
        """Проверка пароля администратора"""
        # 1) Пробуем взять хеш из БД (таблица admin_auth, поле password_hash)
        try:
            resp = self.supabase.table('admin_auth').select('password_hash').limit(1).execute()
            if resp.data:
                db_hash = resp.data[0].get('password_hash')
                if db_hash:
                    return verify_password(password, db_hash)
        except Exception:
            pass
        # 2) Фоллбек на конфиг
        admin_hash = getattr(config, 'ADMIN_PASSWORD_BCRYPT', '') or getattr(config, 'ADMIN_PASSWORD_HASH', '')
        if not admin_hash:
            return False
        return verify_password(password, admin_hash)

    def set_admin_password(self, new_password: str) -> bool:
        """Установить/изменить пароль администратора в БД (таблица admin_auth)."""
        try:
            new_hash = hash_password_secure(new_password)
            # upsert единственной строки
            self.supabase.table('admin_auth').upsert({
                'id': 1,
                'password_hash': new_hash,
                'updated_at': now_msk().isoformat()
            }, on_conflict='id').execute()
            return True
        except Exception:
            try:
                # Попытка создать таблицу и повторить
                self.supabase.rpc('exec_sql', {
                    'sql': "CREATE TABLE IF NOT EXISTS admin_auth (id INT PRIMARY KEY, password_hash TEXT NOT NULL, updated_at TIMESTAMPTZ);"
                }).execute()
            except Exception:
                pass
            try:
                new_hash = hash_password_secure(new_password)
                self.supabase.table('admin_auth').upsert({
                    'id': 1,
                    'password_hash': new_hash,
                    'updated_at': now_msk().isoformat()
                }, on_conflict='id').execute()
                return True
            except Exception:
                return False

    # === Admin session tokens (stateless, HMAC-signed) ===
    def _admin_secret(self) -> bytes:
        s = (getattr(config, 'ADMIN_PASSWORD_BCRYPT', '') or getattr(config, 'ADMIN_PASSWORD_HASH', '') or getattr(config, 'TELEGRAM_BOT_TOKEN', '') or getattr(config, 'SUPABASE_ANON_KEY', '') or 'secret')
        return s.encode('utf-8')

    def _b64url_encode(self, b: bytes) -> str:
        return base64.urlsafe_b64encode(b).rstrip(b'=').decode('ascii')

    def _b64url_decode(self, s: str) -> bytes:
        pad = '=' * (-len(s) % 4)
        return base64.urlsafe_b64decode((s + pad).encode('ascii'))

    def issue_admin_token(self) -> str:
        payload = {
            'iat': int(now_msk().timestamp()),
            'exp': int((now_msk() + timedelta(days=30)).timestamp())
        }
        body = json.dumps(payload, separators=(',', ':')).encode('utf-8')
        b64 = self._b64url_encode(body)
        sig = hmac.new(self._admin_secret(), b64.encode('ascii'), hashlib.sha256).digest()
        return b64 + '.' + self._b64url_encode(sig)

    def verify_admin_token(self, token: str) -> bool:
        try:
            if not token or '.' not in token:
                return False
            b64, sig_b64 = token.split('.', 1)
            expected = hmac.new(self._admin_secret(), b64.encode('ascii'), hashlib.sha256).digest()
            provided = self._b64url_decode(sig_b64)
            if not hmac.compare_digest(expected, provided):
                return False
            payload = json.loads(self._b64url_decode(b64))
            now_ts = int(now_msk().timestamp())
            return int(payload.get('exp', 0)) > now_ts
        except Exception:
            return False

    def revoke_admin_tokens(self) -> None:
        try:
            pass
        except Exception:
            pass

    # === Remember me tokens ===
    def issue_remember_token(self, phone: str) -> str:
        """Выдать токен автологина на 30 дней и сохранить его хеш в БД"""
        try:
            raw_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
            normalized = normalize_phone(phone)
            phone_hash = hash_password(normalize_phone(phone))
            expires_at = (now_msk() + timedelta(days=30)).isoformat()
            self.supabase.table('client_auth_tokens').insert({
                'phone_hash': phone_hash,
                'token_hash': token_hash,
                'client_phone': normalized,
                'expires_at': expires_at,
                'created_at': now_msk().isoformat()
            }).execute()
            return raw_token
        except Exception as e:
            # Таблица может отсутствовать; молча возвращаем пустой токен
            return ""

    def verify_remember_token(self, token: str) -> str:
        """Проверить токен автологина. Возвращает нормализованный телефон или пустую строку"""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            now_iso = now_msk().isoformat()
            resp = self.supabase.table('client_auth_tokens')\
                .select('client_phone, phone_hash, expires_at')\
                .eq('token_hash', token_hash)\
                .gt('expires_at', now_iso)\
                .limit(1)\
                .execute()
            if resp.data:
                cp = resp.data[0].get('client_phone')
                if cp:
                    return cp
                # Фоллбек на случай отсутствия client_phone
                return ""
            return ""
        except Exception:
            return ""

    def revoke_tokens(self, phone: str) -> None:
        """Удалить все токены для телефона"""
        try:
            phone_hash = hash_password(normalize_phone(phone))
            self.supabase.table('client_auth_tokens').delete().eq('phone_hash', phone_hash).execute()
        except Exception:
            pass