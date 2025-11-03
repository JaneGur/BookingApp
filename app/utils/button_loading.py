"""
Универсальный обработчик загрузки для кнопок
Файл: app/utils/button_loading.py
Добавляет спиннер и сообщение при нажатии на любую кнопку
"""
import streamlit as st
from contextlib import contextmanager
from functools import wraps
import time
from typing import Callable, Optional

@contextmanager
def button_loading(message: str = "⏳ Пожалуйста, подождите...", success_message: Optional[str] = None):
    """
    Контекстный менеджер для отображения загрузки при нажатии кнопки
    
    Usage:
        if st.button("Сохранить"):
            with button_loading("💾 Сохранение..."):
                # ваш код
                save_data()
    """
    placeholder = st.empty()
    with placeholder.container():
        with st.spinner(message):
            try:
                yield
                if success_message:
                    placeholder.success(success_message)
                    time.sleep(0.5)
            finally:
                placeholder.empty()

def with_loading(message: str = "⏳ Обработка...", success_msg: Optional[str] = None, show_time: float = 0.3):
    """
    Декоратор для добавления индикатора загрузки к функциям
    
    Usage:
        @with_loading("💾 Сохранение данных...", "✅ Сохранено!")
        def save_booking():
            # ваш код
            return True
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with st.spinner(message):
                start = time.time()
                result = func(*args, **kwargs)
                
                # Минимальная видимость спиннера для UX
                elapsed = time.time() - start
                if elapsed < show_time:
                    time.sleep(show_time - elapsed)
                
                if success_msg and result:
                    st.success(success_msg)
                    time.sleep(0.3)
                
                return result
        return wrapper
    return decorator

class SmartButton:
    """
    Умная кнопка с автоматической индикацией загрузки
    
    Usage:
        btn = SmartButton("Сохранить", loading_msg="💾 Сохранение...")
        if btn.clicked():
            # ваш код здесь автоматически обернут в спиннер
            save_data()
            btn.success("✅ Сохранено!")
    """
    
    def __init__(self, label: str, loading_msg: str = "⏳ Обработка...", 
                 key: Optional[str] = None, **button_kwargs):
        self.label = label
        self.loading_msg = loading_msg
        self.key = key or f"smart_btn_{label}"
        self.button_kwargs = button_kwargs
        self._placeholder = None
        self._is_loading = False
    
    def clicked(self) -> bool:
        """Отрисовка кнопки и проверка клика"""
        if st.button(self.label, key=self.key, **self.button_kwargs):
            self._placeholder = st.empty()
            self._is_loading = True
            return True
        return False
    
    def __enter__(self):
        if self._is_loading and self._placeholder:
            self._spinner = self._placeholder.container().__enter__()
            st.spinner(self.loading_msg).__enter__()
        return self
    
    def __exit__(self, *args):
        if self._is_loading and self._placeholder:
            st.spinner(self.loading_msg).__exit__(*args)
            self._spinner.__exit__(*args)
            self._placeholder.empty()
    
    def success(self, message: str):
        """Показать сообщение успеха"""
        if self._placeholder:
            self._placeholder.success(message)
            time.sleep(0.5)
            self._placeholder.empty()
    
    def error(self, message: str):
        """Показать сообщение об ошибке"""
        if self._placeholder:
            self._placeholder.error(message)
            time.sleep(0.5)
            self._placeholder.empty()

# Предустановленные сообщения для типичных операций
LOADING_MESSAGES = {
    'save': '💾 Сохранение...',
    'delete': '🗑️ Удаление...',
    'create': '✨ Создание...',
    'update': '🔄 Обновление...',
    'send': '📤 Отправка...',
    'load': '📥 Загрузка...',
    'search': '🔍 Поиск...',
    'login': '🔐 Вход в систему...',
    'logout': '🚪 Выход...',
    'payment': '💳 Обработка платежа...',
    'cancel': '❌ Отмена...',
    'confirm': '✅ Подтверждение...',
    'connect': '🔗 Подключение...',
    'disconnect': '🔌 Отключение...',
}

def quick_loading(operation: str) -> str:
    """Получить предустановленное сообщение для операции"""
    return LOADING_MESSAGES.get(operation, '⏳ Обработка...')


# ============= ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ =============

# 1. Контекстный менеджер
def example_context_manager():
    if st.button("Сохранить данные"):
        with button_loading("💾 Сохранение данных...", "✅ Данные сохранены!"):
            # Ваш код сохранения
            time.sleep(1)  # имитация работы
            save_to_database()

# 2. Декоратор
def example_decorator():
    @with_loading("🔐 Проверка пароля...", "✅ Вход выполнен!")
    def check_password(password):
        # Логика проверки
        return validate_password(password)
    
    if st.button("Войти"):
        result = check_password(password)

# 3. Умная кнопка
def example_smart_button():
    btn = SmartButton("Создать запись", 
                     loading_msg="✨ Создание записи...",
                     type="primary", 
                     use_container_width=True)
    
    if btn.clicked():
        with btn:
            success = create_booking(data)
            if success:
                btn.success("✅ Запись создана!")
            else:
                btn.error("❌ Ошибка создания")

# 4. Быстрое сообщение
def example_quick():
    if st.button("Удалить"):
        with button_loading(quick_loading('delete')):
            delete_item()