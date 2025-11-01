import secrets
from datetime import datetime, timedelta
from typing import Optional
from utils.datetime_helpers import now_msk, combine_msk

def generate_temporary_password() -> str:
    """Генерация временного пароля"""
    return secrets.token_urlsafe(8)

def calculate_time_until(date_str: str, time_str: str) -> timedelta:
    """Вычисление времени до события"""
    try:
        event_datetime = combine_msk(date_str, time_str)
        return event_datetime - now_msk()
    except:
        return timedelta(0)