from datetime import datetime, timedelta
from typing import Optional
from utils.datetime_helpers import now_msk, combine_msk

def format_date(date_str: str, format_str: str = '%d.%m.%Y') -> str:
    """Форматирование даты с обработкой ошибок"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime(format_str)
    except:
        return date_str

def format_datetime_relative(date_str: str, time_str: str) -> str:
    """Форматирование даты/времени относительно текущего момента"""
    try:
        event_datetime = combine_msk(date_str, time_str)
        now = now_msk()
        
        if event_datetime.date() == now.date():
            return f"Сегодня в {time_str}"
        elif event_datetime.date() == (now + timedelta(days=1)).date():
            return f"Завтра в {time_str}"
        elif event_datetime.date() == (now - timedelta(days=1)).date():
            return f"Вчера в {time_str}"
        else:
            return f"{format_date(date_str)} в {time_str}"
    except:
        return f"{date_str} {time_str}"

def format_timedelta(td: timedelta) -> str:
    """Форматирование timedelta в читаемый вид"""
    if td.total_seconds() < 0:
        return "Прошло"
    
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days} дн.")
    if hours > 0:
        parts.append(f"{hours} ч.")
    if minutes > 0 or not parts:
        parts.append(f"{minutes} мин.")
    
    return " ".join(parts)

def get_month_end(year: int, month: int) -> str:
    """Получение последнего дня месяца"""
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    month_end = next_month - timedelta(days=1)
    return month_end.strftime('%Y-%m-%d')

def get_weekday_name(date_str: str) -> str:
    """Получение названия дня недели"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        weekday_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        return weekday_names[date_obj.weekday()]
    except:
        return ""