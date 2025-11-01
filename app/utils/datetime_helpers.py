from datetime import datetime
from zoneinfo import ZoneInfo

MSK_TZ = ZoneInfo("Europe/Moscow")

def now_msk() -> datetime:
    return datetime.now(MSK_TZ)

def combine_msk(date_str: str, time_str: str) -> datetime:
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    return dt.replace(tzinfo=MSK_TZ)
