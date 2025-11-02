"""
Оптимизированное кэширование для повышения производительности
"""
import streamlit as st
from functools import wraps
from typing import Any, Callable
import hashlib
import json

def smart_cache(ttl: int = 300, show_spinner: bool = False):
    """
    Умное кэширование с автоматической инвалидацией
    """
    def decorator(func: Callable) -> Callable:
        @st.cache_data(ttl=ttl, show_spinner=show_spinner)
        def cached_func(*args, **kwargs):
            return func(*args, **kwargs)
        return cached_func
    return decorator

def cache_with_key(key_func: Callable = None, ttl: int = 300):
    """
    Кэширование с кастомным ключом
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            if cache_key not in st.session_state:
                st.session_state[cache_key] = {
                    'data': func(*args, **kwargs),
                    'timestamp': st.session_state.get('_cache_time', 0)
                }
            
            return st.session_state[cache_key]['data']
        return wrapper
    return decorator

# Глобальный кэш для сессии (быстрее чем st.cache_data)
class SessionCache:
    """Кэш на основе session_state для мгновенного доступа"""
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        cache_dict = st.session_state.get('_session_cache', {})
        return cache_dict.get(key, default)
    
    @staticmethod
    def set(key: str, value: Any, ttl: int = 300):
        if '_session_cache' not in st.session_state:
            st.session_state._session_cache = {}
        
        st.session_state._session_cache[key] = {
            'value': value,
            'expires': st.session_state.get('_cache_time', 0) + ttl
        }
    
    @staticmethod
    def invalidate(pattern: str = None):
        if pattern:
            st.session_state._session_cache = {
                k: v for k, v in st.session_state.get('_session_cache', {}).items()
                if pattern not in k
            }
        else:
            st.session_state._session_cache = {}

# Декоратор для быстрого кэширования в session_state
def session_cached(ttl: int = 300):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Генерируем уникальный ключ
            key_data = f"{func.__name__}_{args}_{kwargs}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            cached = SessionCache.get(cache_key)
            if cached is not None:
                return cached['value']
            
            result = func(*args, **kwargs)
            SessionCache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator