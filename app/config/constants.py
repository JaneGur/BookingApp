BOOKING_RULES = {
    "MIN_ADVANCE_HOURS": 1,
    "MIN_CANCEL_MINUTES": 30,
    "MAX_DAYS_AHEAD": 30,
}

STATUS_DISPLAY = {
    'confirmed': {'emoji': '✅', 'text': 'Подтверждена', 'color': '#88c8bc', 'bg_color': '#f0f9f7'},
    'pending_payment': {'emoji': '🟡', 'text': 'Ожидает оплаты', 'color': '#e6a700', 'bg_color': '#fff8e1'},
    'cancelled': {'emoji': '❌', 'text': 'Отменена', 'color': '#ff6b6b', 'bg_color': '#fff5f5'},
    'completed': {'emoji': '✅', 'text': 'Завершена', 'color': '#6ba292', 'bg_color': '#f0f9f7'}
}

WEEKDAY_MAP = {
    '0': 'Вс', '1': 'Пн', '2': 'Вт', 
    '3': 'Ср', '4': 'Чт', '5': 'Пт', '6': 'Сб'
}

DEFAULT_SETTINGS = {
    'work_start': '09:00',
    'work_end': '18:00', 
    'session_duration': 60,
    'break_duration': 15,
    'info_title': 'ℹ️ Информация',
    'info_work_hours': '🕐 Рабочее время:\n09:00 - 18:00',
    'info_session_duration': '⏱️ Длительность консультации:\n60 минут',
    'info_format': '💻 Формат:\nОнлайн или в кабинете',
    'info_contacts': '📞 Контакты:\n📱 +7 (999) 123-45-67\n📧 hello@psychologist.ru\n🌿 psychologist.ru',
    'info_additional': ''
}

STATUS_DISPLAY = {
    'pending_payment': {
        'text': '🟡 Ожидает оплаты',
        'emoji': '🟡',
        'color': '#f59e0b',
        'bg_color': '#fffbeb'
    },
    'confirmed': {
        'text': '✅ Подтверждён',
        'emoji': '✅', 
        'color': '#10b981',
        'bg_color': '#ecfdf5'
    },
    'completed': {
        'text': '✅ Завершён',
        'emoji': '✅',
        'color': '#059669', 
        'bg_color': '#ecfdf5'
    },
    'cancelled': {
        'text': '❌ Отменён',
        'emoji': '❌',
        'color': '#ef4444',
        'bg_color': '#fef2f2'
    }
}