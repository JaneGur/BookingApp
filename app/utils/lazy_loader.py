"""
Ленивая загрузка данных для улучшения отзывчивости UI
"""
import streamlit as st
from typing import Callable, Any
from concurrent.futures import ThreadPoolExecutor
import time

class LazyLoader:
    """Загрузчик данных с отложенной инициализацией"""
    
    def __init__(self, loader_func: Callable, *args, **kwargs):
        self.loader_func = loader_func
        self.args = args
        self.kwargs = kwargs
        self._data = None
        self._loaded = False
        self._loading = False
    
    @property
    def data(self):
        if not self._loaded and not self._loading:
            self._loading = True
            self._data = self.loader_func(*self.args, **self.kwargs)
            self._loaded = True
            self._loading = False
        return self._data
    
    def is_loaded(self) -> bool:
        return self._loaded
    
    def reset(self):
        self._loaded = False
        self._data = None

class BackgroundLoader:
    """Фоновая загрузка тяжелых данных"""
    
    _executor = ThreadPoolExecutor(max_workers=3)
    
    @classmethod
    def load_async(cls, key: str, loader_func: Callable, *args, **kwargs):
        """Запустить загрузку в фоне"""
        if key not in st.session_state:
            st.session_state[key] = {
                'status': 'loading',
                'data': None,
                'error': None
            }
            
            def load_and_store():
                try:
                    result = loader_func(*args, **kwargs)
                    st.session_state[key] = {
                        'status': 'loaded',
                        'data': result,
                        'error': None
                    }
                except Exception as e:
                    st.session_state[key] = {
                        'status': 'error',
                        'data': None,
                        'error': str(e)
                    }
            
            cls._executor.submit(load_and_store)
    
    @classmethod
    def get_status(cls, key: str) -> dict:
        """Получить статус загрузки"""
        return st.session_state.get(key, {'status': 'not_started', 'data': None, 'error': None})
    
    @classmethod
    def is_ready(cls, key: str) -> bool:
        """Проверить готовность данных"""
        status = cls.get_status(key)
        return status['status'] == 'loaded'

# Прогрессивная загрузка списков
def render_with_pagination(items: list, page_size: int = 20, key: str = "pagination"):
    """Отрисовка списка с пагинацией для ускорения"""
    if not items:
        return []
    
    # Инициализация страницы
    page_key = f"{key}_page"
    if page_key not in st.session_state:
        st.session_state[page_key] = 0
    
    total_pages = (len(items) - 1) // page_size + 1
    current_page = st.session_state[page_key]
    
    # Показываем только текущую страницу
    start_idx = current_page * page_size
    end_idx = min(start_idx + page_size, len(items))
    current_items = items[start_idx:end_idx]
    
    # Навигация
    if total_pages > 1:
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button("⏮️ Первая", disabled=current_page == 0, key=f"{key}_first"):
                st.session_state[page_key] = 0
                st.rerun()
        
        with col2:
            if st.button("◀️ Назад", disabled=current_page == 0, key=f"{key}_prev"):
                st.session_state[page_key] = max(0, current_page - 1)
                st.rerun()
        
        with col3:
            st.markdown(f"<center>Страница {current_page + 1} из {total_pages}</center>", 
                       unsafe_allow_html=True)
        
        with col4:
            if st.button("Вперед ▶️", disabled=current_page >= total_pages - 1, key=f"{key}_next"):
                st.session_state[page_key] = min(total_pages - 1, current_page + 1)
                st.rerun()
        
        with col5:
            if st.button("Последняя ⏭️", disabled=current_page >= total_pages - 1, key=f"{key}_last"):
                st.session_state[page_key] = total_pages - 1
                st.rerun()
    
    return current_items

# Виртуальный скроллинг для больших списков
def virtual_scroll(items: list, item_height: int = 100, visible_count: int = 10, key: str = "scroll"):
    """Виртуальный скроллинг - отрисовка только видимых элементов"""
    if not items:
        return []
    
    scroll_key = f"{key}_scroll"
    if scroll_key not in st.session_state:
        st.session_state[scroll_key] = 0
    
    # Рассчитываем диапазон видимых элементов
    start_idx = st.session_state[scroll_key]
    end_idx = min(start_idx + visible_count, len(items))
    
    visible_items = items[start_idx:end_idx]
    
    # Кнопки прокрутки
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬆️ Вверх", disabled=start_idx == 0, key=f"{key}_up"):
            st.session_state[scroll_key] = max(0, start_idx - visible_count)
            st.rerun()
    
    with col2:
        st.caption(f"Показано {start_idx + 1}-{end_idx} из {len(items)}")
    
    with col3:
        if st.button("⬇️ Вниз", disabled=end_idx >= len(items), key=f"{key}_down"):
            st.session_state[scroll_key] = min(len(items) - visible_count, start_idx + visible_count)
            st.rerun()
    
    return visible_items