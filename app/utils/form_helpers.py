"""
Оптимизированные формы с минимизацией rerun
"""
import streamlit as st
from typing import Callable, Dict, Any
import time

class OptimizedForm:
    """Форма с оптимизированной обработкой"""
    
    def __init__(self, form_key: str):
        self.form_key = form_key
        self.data = {}
        self.submitted = False
    
    def __enter__(self):
        self._form_container = st.form(self.form_key, clear_on_submit=False)
        self._form_container.__enter__()
        return self
    
    def __exit__(self, *args):
        self._form_container.__exit__(*args)
    
    def submit_button(self, label: str, **kwargs):
        self.submitted = st.form_submit_button(label, **kwargs)
        return self.submitted

class FormProcessor:
    """Процессор форм с кэшированием и валидацией"""
    
    @staticmethod
    def process_with_spinner(
        form_data: dict,
        processor_func: Callable,
        success_message: str = "✅ Успешно сохранено",
        spinner_text: str = "⏳ Обработка...",
        rerun_on_success: bool = True
    ) -> bool:
        """
        Обработка формы с визуальной индикацией
        
        Args:
            form_data: Данные формы
            processor_func: Функция обработки, должна возвращать (success, message)
            success_message: Сообщение при успехе
            spinner_text: Текст спиннера
            rerun_on_success: Перезагружать ли страницу при успехе
        """
        with st.spinner(spinner_text):
            # Имитируем минимальную задержку для плавности
            time.sleep(0.1)
            
            try:
                success, message = processor_func(form_data)
                
                if success:
                    st.success(success_message if not message else message)
                    
                    # Кэшируем успешный результат
                    st.session_state['_last_success'] = {
                        'message': message or success_message,
                        'time': time.time()
                    }
                    
                    if rerun_on_success:
                        time.sleep(0.3)  # Даем пользователю увидеть сообщение
                        st.rerun()
                    
                    return True
                else:
                    st.error(message or "❌ Ошибка обработки")
                    return False
                    
            except Exception as e:
                st.error(f"❌ Ошибка: {str(e)}")
                return False

# Декоратор для оптимизации обработчиков кнопок
def optimized_button_handler(
    spinner_text: str = "⏳ Обработка...",
    success_message: str = "✅ Готово",
    show_success_duration: float = 0.5,
    rerun: bool = True
):
    """
    Декоратор для оптимизированной обработки кнопок
    
    Использование:
        @optimized_button_handler("Создание записи...", "✅ Запись создана")
        def create_booking(data):
            # ваш код
            return True, "Успех"
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # Показываем spinner только если операция долгая
            start_time = time.time()
            
            with st.spinner(spinner_text):
                result = func(*args, **kwargs)
                
                # Если операция быстрая, добавляем минимальную задержку для UX
                elapsed = time.time() - start_time
                if elapsed < 0.2:
                    time.sleep(0.2 - elapsed)
            
            # Обработка результата
            if isinstance(result, tuple):
                success, message = result
            else:
                success = bool(result)
                message = success_message
            
            if success:
                st.success(message)
                if show_success_duration > 0:
                    time.sleep(show_success_duration)
                if rerun:
                    st.rerun()
            else:
                st.error(message or "❌ Ошибка выполнения")
            
            return result
        return wrapper
    return decorator

# Батчинг операций для снижения количества rerun
class BatchOperations:
    """Батчинг нескольких операций в одну"""
    
    def __init__(self):
        self.operations = []
        self.results = []
    
    def add(self, operation: Callable, *args, **kwargs):
        """Добавить операцию в очередь"""
        self.operations.append((operation, args, kwargs))
    
    def execute_all(self, show_progress: bool = True) -> list:
        """Выполнить все операции"""
        self.results = []
        
        if show_progress and len(self.operations) > 1:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        for i, (op, args, kwargs) in enumerate(self.operations):
            if show_progress and len(self.operations) > 1:
                progress = (i + 1) / len(self.operations)
                progress_bar.progress(progress)
                status_text.text(f"Выполнение {i + 1} из {len(self.operations)}...")
            
            try:
                result = op(*args, **kwargs)
                self.results.append({'success': True, 'result': result})
            except Exception as e:
                self.results.append({'success': False, 'error': str(e)})
        
        if show_progress and len(self.operations) > 1:
            progress_bar.empty()
            status_text.empty()
        
        return self.results
    
    def clear(self):
        """Очистить очередь"""
        self.operations = []
        self.results = []

# Умная форма с автосохранением в session_state
class SmartForm:
    """Форма с автосохранением состояния"""
    
    def __init__(self, form_id: str, auto_save: bool = True):
        self.form_id = form_id
        self.auto_save = auto_save
        self.state_key = f"_form_state_{form_id}"
        
        # Восстанавливаем состояние
        if self.state_key not in st.session_state:
            st.session_state[self.state_key] = {}
    
    def text_input(self, label: str, key: str = None, **kwargs):
        """Text input с автосохранением"""
        field_key = key or label
        default_value = st.session_state[self.state_key].get(field_key, kwargs.get('value', ''))
        
        value = st.text_input(label, value=default_value, key=f"{self.form_id}_{field_key}", **kwargs)
        
        if self.auto_save:
            st.session_state[self.state_key][field_key] = value
        
        return value
    
    def get_data(self) -> dict:
        """Получить все данные формы"""
        return st.session_state[self.state_key].copy()
    
    def clear(self):
        """Очистить сохраненные данные"""
        st.session_state[self.state_key] = {}
    
    def restore_defaults(self, defaults: dict):
        """Восстановить значения по умолчанию"""
        st.session_state[self.state_key] = defaults.copy()