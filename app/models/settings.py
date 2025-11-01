from dataclasses import dataclass
from typing import Optional

@dataclass
class SystemSettings:
    id: int = 1
    work_start: str = "09:00"
    work_end: str = "18:00"
    session_duration: int = 60
    break_duration: int = 15
    info_title: str = "ℹ️ Информация"
    info_work_hours: str = "🕐 Рабочее время:\n09:00 - 18:00"
    info_session_duration: str = "⏱️ Длительность консультации:\n60 минут"
    info_format: str = "💻 Формат:\nОнлайн или в кабинете"
    info_contacts: str = "📞 Контакты:\n📱 +7 (999) 123-45-67\n📧 hello@psychologist.ru\n🌿 psychologist.ru"
    info_additional: str = ""
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SystemSettings':
        return cls(
            id=data.get('id', 1),
            work_start=data.get('work_start', '09:00'),
            work_end=data.get('work_end', '18:00'),
            session_duration=data.get('session_duration', 60),
            break_duration=data.get('break_duration', 15),
            info_title=data.get('info_title', 'ℹ️ Информация'),
            info_work_hours=data.get('info_work_hours', '🕐 Рабочее время:\n09:00 - 18:00'),
            info_session_duration=data.get('info_session_duration', '⏱️ Длительность консультации:\n60 минут'),
            info_format=data.get('info_format', '💻 Формат:\nОнлайн или в кабинете'),
            info_contacts=data.get('info_contacts', '📞 Контакты:\n📱 +7 (999) 123-45-67\n📧 hello@psychologist.ru\n🌿 psychologist.ru'),
            info_additional=data.get('info_additional', '')
        )