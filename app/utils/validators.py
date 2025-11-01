import re
import hashlib
import streamlit as st
from typing import Tuple
import bcrypt

def hash_password(password: str) -> str:
    """Хеширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()

def normalize_phone(phone: str) -> str:
    """Нормализация номера телефона"""
    return re.sub(r'\D', '', phone)

def format_phone(phone: str) -> str:
    """Форматирование телефона для отображения"""
    clean = normalize_phone(phone)
    if len(clean) == 11 and clean.startswith('7'):
        return f"+7 ({clean[1:4]}) {clean[4:7]}-{clean[7:9]}-{clean[9:]}"
    elif len(clean) == 10:
        return f"+7 ({clean[0:3]}) {clean[3:6]}-{clean[6:8]}-{clean[8:]}"
    return phone

def validate_phone(phone: str) -> Tuple[bool, str]:
    """Валидация телефона с детальной проверкой"""
    clean = normalize_phone(phone)
    if len(clean) < 10:
        return False, "❌ Номер слишком короткий"
    if len(clean) > 11:
        return False, "❌ Номер слишком длинный"
    if not clean.isdigit():
        return False, "❌ Только цифры"
    if len(clean) == 11 and not clean.startswith('7'):
        return False, "❌ Неверный формат (должен начинаться с 7)"
    return True, "✅ Корректный номер"

def validate_email(email: str) -> Tuple[bool, str]:
    """Валидация email с детальной проверкой"""
    if not email:
        return True, "ℹ️ Email не обязателен"
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, "✅ Email корректен"
    return False, "❌ Неверный формат email"

def hash_password_secure(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode()

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        if stored_hash.startswith("$2a$") or stored_hash.startswith("$2b$") or stored_hash.startswith("$2y$"):
            return bcrypt.checkpw(password.encode(), stored_hash.encode())
        return hashlib.sha256(password.encode()).hexdigest() == stored_hash
    except Exception:
        return False