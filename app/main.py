import streamlit as st
from config.settings import config
from ui.styles import load_custom_css
from core.database import db_manager
from core.session_state import init_session_state
from core.auth import AuthManager
from ui.pages.public_booking import render_public_booking
from ui.pages.admin_panel import render_admin_panel
from ui.pages.client_cabinet import render_client_cabinet
from ui.pages.auth_forms import render_auth_forms

# --- Query params helpers (compat for older Streamlit)
def _get_query_param(key: str):
    try:
        return st.query_params.get(key)
    except Exception:
        try:
            return st.experimental_get_query_params().get(key, [None])[0]
        except Exception:
            return None

def _set_query_param(key: str, value: str):
    try:
        st.query_params[key] = value
    except Exception:
        try:
            params = st.experimental_get_query_params()
            params[key] = value
            st.experimental_set_query_params(**params)
        except Exception:
            pass

def _pop_query_param(key: str):
    try:
        st.query_params.pop(key, None)
    except Exception:
        try:
            params = st.experimental_get_query_params()
            if key in params:
                params.pop(key)
                st.experimental_set_query_params(**params)
        except Exception:
            pass

def setup_sidebar():
    """Настройка боковой панели - ИСПРАВЛЕНО"""
    with st.sidebar:
        st.markdown("# 🌿 Навигация")
        
        # Проверяем состояние авторизации
        is_client = st.session_state.get('client_logged_in', False)
        is_admin = st.session_state.get('admin_logged_in', False)
        
        if is_client:
            setup_client_sidebar()
        elif is_admin:
            setup_admin_sidebar()
        else:
            setup_public_sidebar()
        
        setup_admin_section()

def setup_client_sidebar():
    """Боковая панель для клиента - ИСПРАВЛЕНО"""
    if st.session_state.get('client_name'):
        st.markdown(f"### 👋 {st.session_state.client_name}!")

    # Статус Telegram
    from services.notification_service import NotificationService
    notification_service = NotificationService()
    
    client_phone = st.session_state.get('client_phone', '')
    if client_phone:
        telegram_connected = notification_service.get_client_telegram_chat_id(client_phone)
        if telegram_connected:
            st.success("🔔 Уведомления подключены")
        else:
            st.warning("🔕 Нет уведомлений")

    st.markdown("---")
    
    # УНИКАЛЬНЫЙ ключ для кнопки выхода
    if st.button("🚪 Выйти", width='stretch', key="sidebar_client_logout_btn"):
        try:
            auth = AuthManager()
            if client_phone:
                auth.revoke_tokens(client_phone)
            st.query_params.clear()
        except Exception:
            pass
        
        from core.session_state import client_logout
        client_logout()
        st.rerun()

def setup_admin_sidebar():
    """Боковая панель для администратора - ИСПРАВЛЕНО"""
    st.markdown("### 📊 Статистика")
    
    # Кэшируем статистику
    @st.cache_data(ttl=60, show_spinner=False)
    def get_cached_stats():
        from services.analytics_service import AnalyticsService
        analytics_service = AnalyticsService()
        return analytics_service.get_stats()
    
    total, upcoming, this_month, this_week = get_cached_stats()
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("📋 Всего", total)
    with col_m2:
        st.metric("⏰ Предстоящих", upcoming)
    
    col_m3, col_m4 = st.columns(2)
    with col_m3:
        st.metric("📅 За месяц", this_month)
    with col_m4:
        st.metric("📆 За неделю", this_week)
    
    st.divider()
    st.markdown("### 👩‍💼 Администратор")
    st.success("✅ Вы зашли как администратор")
    
    # УНИКАЛЬНЫЙ ключ для кнопки выхода админа
    if st.button("🚪 Выйти", width='stretch', key="sidebar_admin_logout_btn"):
        from core.session_state import admin_logout
        try:
            auth = AuthManager()
            auth.revoke_admin_tokens()
            st.query_params.pop('at', None)
        except Exception:
            pass
        
        admin_logout()
        st.rerun()

def setup_public_sidebar():
    """Боковая панель для публичного доступа - ИСПРАВЛЕНО"""
    st.markdown("### 👤 Личный кабинет")
    
    # КРИТИЧНО: Инициализируем значение по умолчанию ОДИН РАЗ
    if 'public_auth_action' not in st.session_state:
        st.session_state.public_auth_action = "🔐 Войти"
    
    # Используем session_state как source of truth
    current_action = st.session_state.public_auth_action
    
    # Радиокнопка БЕЗ callback - изменения обрабатываем вручную
    action = st.radio(
        "Выберите действие",
        ["🔐 Войти", "📝 Регистрация", "🔑 Забыли пароль?"],
        index=["🔐 Войти", "📝 Регистрация", "🔑 Забыли пароль?"].index(current_action),
        key="sidebar_public_auth_radio"  # УНИКАЛЬНЫЙ ключ
    )
    
    # Обрабатываем изменение действия
    if action != current_action:
        st.session_state.public_auth_action = action
        
        # Обновляем флаги форм в зависимости от выбора
        if action == "🔐 Войти":
            st.session_state.show_client_login = True
            st.session_state.show_client_registration = False
            st.session_state.show_password_reset = False
        elif action == "📝 Регистрация":
            st.session_state.show_client_login = False
            st.session_state.show_client_registration = True
            st.session_state.show_password_reset = False
        else:  # "🔑 Забыли пароль?"
            st.session_state.show_client_login = False
            st.session_state.show_client_registration = False
            st.session_state.show_password_reset = True
        
        st.rerun()

def setup_admin_section():
    """Раздел администратора в сайдбаре - ИСПРАВЛЕНО"""
    st.markdown("---")
    
    is_client = st.session_state.get('client_logged_in', False)
    is_admin = st.session_state.get('admin_logged_in', False)
    
    # Показываем вход для админа только если никто не авторизован
    if not is_client and not is_admin:
        st.markdown("### 👩‍💼 Администратор")
        
        # УНИКАЛЬНЫЙ ключ для кнопки
        if st.button("🔐 Вход для администратора", width='stretch', type="secondary", key="sidebar_admin_login_btn"):
            st.session_state.show_admin_login = True
            st.rerun()
        
        # Форма входа админа
        if st.session_state.get('show_admin_login', False):
            with st.form("admin_sidebar_login_form", clear_on_submit=False):  # УНИКАЛЬНЫЙ ключ
                password = st.text_input("Пароль администратора", type="password", key="sidebar_admin_pwd")
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("Войти", width='stretch')
                with col2:
                    cancel = st.form_submit_button("Отмена", width='stretch')
                
                if submit:
                    if password:
                        auth_manager = AuthManager()
                        if auth_manager.check_admin_password(password):
                            from core.session_state import admin_login
                            admin_login()
                            st.success("✅ Добро пожаловать!")
                            
                            # Выдаём админ-токен
                            try:
                                at = auth_manager.issue_admin_token()
                                if at:
                                    st.query_params["at"] = at
                            except Exception:
                                pass
                            
                            st.rerun()
                        else:
                            st.error("❌ Неверный пароль!")
                    else:
                        st.warning("⚠️ Введите пароль")
                
                if cancel:
                    st.session_state.show_admin_login = False
                    st.rerun()

def main():
    """Главная функция приложения - ИСПРАВЛЕНО"""
    # Инициализация приложения
    st.set_page_config(**config.PAGE_CONFIG)
    load_custom_css()
    
    # Инициализация базы данных
    if db_manager.get_client() is None:
        st.error("❌ Не удалось подключиться к базе данных")
        return
    
    # Инициализация состояния
    init_session_state()
    
    # КРИТИЧНО: Автовход ТОЛЬКО ОДИН РАЗ за сессию
    if '_auto_login_checked' not in st.session_state:
        st.session_state._auto_login_checked = True
        perform_auto_login()
    
    # Инициализация таблицы аутентификации
    if not st.session_state.get('auth_table_initialized'):
        with st.spinner("🔐 Инициализация системы безопасности..."):
            if db_manager.init_auth_table():
                st.session_state.auth_table_initialized = True
            else:
                st.error("❌ Ошибка инициализации системы безопасности")
                st.stop()
    
    # Настройка боковой панели
    setup_sidebar()
    
    # Отображение форм аутентификации если нужно
    show_login = st.session_state.get('show_client_login', False)
    show_reg = st.session_state.get('show_client_registration', False)
    show_reset = st.session_state.get('show_password_reset', False)
    
    if show_login or show_reg or show_reset:
        render_auth_forms()
        return
    
    # Маршрутизация по ролям
    is_admin = st.session_state.get('admin_logged_in', False)
    is_client = st.session_state.get('client_logged_in', False)
    
    if is_admin:
        render_admin_panel()
    elif is_client:
        render_client_cabinet()
    else:
        render_public_booking()

    # Глобальный футер с документами
    render_footer()

def perform_auto_login():
    """Выполнить автовход по токенам - вызывается ОДИН РАЗ"""
    is_client = st.session_state.get('client_logged_in', False)
    is_admin = st.session_state.get('admin_logged_in', False)
    
    # Если уже авторизованы - пропускаем
    if is_client or is_admin:
        return
    
    # Проверка админ-токена
    try:
        at = st.query_params.get('at')
        if at:
            auth = AuthManager()
            if auth.verify_admin_token(at):
                from core.session_state import admin_login
                admin_login()
                return  # Успешный вход админа
    except Exception as e:
        print(f"Ошибка проверки админ-токена: {e}")
    
    # Проверка клиент-токена
    try:
        token = st.query_params.get('rt')
        if token:
            auth = AuthManager()
            phone_norm = auth.verify_remember_token(token)
            if phone_norm:
                from services.client_service import ClientService
                cs = ClientService()
                info = cs.get_profile(phone_norm)
                
                st.session_state.client_logged_in = True
                st.session_state.client_phone = phone_norm
                st.session_state.client_name = (info['client_name'] if info else '')
                st.session_state.current_tab = "🏠 Главная"
    except Exception as e:
        print(f"Ошибка проверки клиент-токена: {e}")

def render_footer():
    try:
        from core.database import db_manager
        sb = db_manager.get_client()
        policy_url = None
        offer_url = None
        if sb is not None:
            resp = sb.table('documents').select('doc_type, url, is_active, updated_at')\
                .eq('is_active', True).execute()
            rows = resp.data or []
            # Берём последние активные policy/offer
            for doc_type in ('policy', 'offer'):
                docs = [r for r in rows if (r.get('doc_type') == doc_type and r.get('url'))]
                docs.sort(key=lambda r: r.get('updated_at') or '', reverse=True)
                if docs:
                    if doc_type == 'policy':
                        policy_url = docs[0]['url']
                    else:
                        offer_url = docs[0]['url']
        st.markdown('---')
        links = []
        if policy_url:
            links.append(f"[Политика конфиденциальности]({policy_url})")
        else:
            links.append("Политика конфиденциальности (скоро)")
        if offer_url:
            links.append(f"[Публичная оферта]({offer_url})")
        else:
            links.append("Публичная оферта (скоро)")
        st.markdown(" · ".join(links))
    except Exception:
        # Тихо игнорируем ошибки футера
        pass

if __name__ == "__main__":
    main()