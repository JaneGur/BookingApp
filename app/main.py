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
    """Настройка боковой панели"""
    with st.sidebar:
        st.markdown("# 🌿 Навигация")
        
        if st.session_state.client_logged_in:
            setup_client_sidebar()
        elif st.session_state.admin_logged_in:
            setup_admin_sidebar()
        else:
            setup_public_sidebar()
        
        setup_admin_section()

def setup_client_sidebar():
    """Боковая панель для клиента"""
    if st.session_state.client_name:
        st.markdown(f"### 👋 {st.session_state.client_name}!")

    # Статус Telegram (оставляем пользователю)
    from services.notification_service import NotificationService
    notification_service = NotificationService()
    telegram_connected = notification_service.get_client_telegram_chat_id(st.session_state.client_phone)
    if telegram_connected:
        st.success("🔔 Уведомления подключены")
    else:
        st.warning("🔕 Нет уведомлений")

    st.markdown("---")
    # Только кнопка выхода без дополнительных блоков безопасности
    if st.button("🚪 Выйти", width='stretch'):
        # Отзываем remember-me токены и очищаем query-параметры
        try:
            auth = AuthManager()
            if st.session_state.client_phone:
                auth.revoke_tokens(st.session_state.client_phone)
            # Очистка query-параметров
            st.query_params.clear()
        except Exception:
            pass
        from core.session_state import client_logout
        client_logout()
        st.rerun()

def setup_admin_sidebar():
    """Боковая панель для администратора"""
    st.markdown("### 📊 Статистика")
    from services.analytics_service import AnalyticsService
    analytics_service = AnalyticsService()
    total, upcoming, this_month, this_week = analytics_service.get_stats()
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
    
    if st.button("🚪 Выйти", width='stretch'):
        from core.session_state import admin_logout
        try:
            auth = AuthManager()
            auth.revoke_admin_tokens()
            _pop_query_param('at')
        except Exception:
            pass
        admin_logout()
        st.rerun()

def setup_public_sidebar():
    """Боковая панель для публичного доступа"""
    st.markdown("### 👤 Личный кабинет")
    
    action = st.radio(
        "Выберите действие",
        ["🔐 Войти", "📝 Регистрация", "🔑 Забыли пароль?"],
        index=0,
        key="public_auth_action"
    )
    # Мгновенная навигация при смене выбора
    prev_action = st.session_state.get('public_auth_action_prev')
    if prev_action is None:
        st.session_state.public_auth_action_prev = action
    elif action != prev_action:
        if action.startswith("🔐"):
            st.session_state.show_client_login = True
            st.session_state.show_client_registration = False
            st.session_state.show_password_reset = False
        elif action.startswith("📝"):
            st.session_state.show_client_login = False
            st.session_state.show_client_registration = True
            st.session_state.show_password_reset = False
        else:
            st.session_state.show_client_login = False
            st.session_state.show_client_registration = False
            st.session_state.show_password_reset = True
        st.session_state.public_auth_action_prev = action
        st.rerun()

def setup_admin_section():
    """Раздел администратора в сайдбаре"""
    st.markdown("---")
    
    if not st.session_state.client_logged_in and not st.session_state.admin_logged_in:
        st.markdown("### 👩‍💼 Администратор")
        
        if st.button("🔐 Вход для администратора", width='stretch', type="secondary"):
            st.session_state.show_admin_login = True
            st.rerun()
        
        if st.session_state.show_admin_login:
            with st.form("admin_sidebar_login", clear_on_submit=True):
                password = st.text_input("Пароль администратора", type="password")
                submit = st.form_submit_button("Войти", width='stretch')
                
                if submit:
                    auth_manager = AuthManager()
                    if password and auth_manager.check_admin_password(password):
                        from core.session_state import admin_login
                        admin_login()
                        st.success("✅ Добро пожаловать!")
                        # Выдаём админ-токен и фиксируем в URL для автологина при обновлении страницы
                        try:
                            at = auth_manager.issue_admin_token()
                            if at:
                                _set_query_param("at", at)
                        except Exception:
                            pass
                        st.rerun()
                    elif password:
                        st.error("❌ Неверный пароль!")
            
            if st.button("❌ Отмена", width='stretch', type="secondary"):
                st.session_state.show_admin_login = False
                st.rerun()

def main():
    """Главная функция приложения"""
    # Инициализация приложения
    st.set_page_config(**config.PAGE_CONFIG)
    load_custom_css()
    
    # Инициализация базы данных
    if db_manager.get_client() is None:
        st.error("❌ Не удалось подключиться к базе данных")
        return
    
    # Инициализация состояния
    init_session_state()
    
    # Автовход по remember-me токену из URL (если не авторизованы)
    if not (st.session_state.client_logged_in or st.session_state.admin_logged_in):
        try:
            at = _get_query_param('at')
            if at:
                auth = AuthManager()
                if auth.verify_admin_token(at):
                    from core.session_state import admin_login
                    admin_login()
        except Exception:
            pass
        try:
            token = _get_query_param('rt')
            if token:
                auth = AuthManager()
                phone_norm = auth.verify_remember_token(token)
                if phone_norm:
                    # Получаем имя клиента и входим
                    from services.client_service import ClientService
                    cs = ClientService()
                    info = cs.get_client_info(phone_norm)
                    st.session_state.client_logged_in = True
                    st.session_state.client_phone = phone_norm
                    st.session_state.client_name = (info['client_name'] if info else st.session_state.get('client_name', ''))
                    # Откроем кабинет на Главной
                    st.session_state.current_tab = "🏠 Главная"
                    st.query_params["rt"] = token
        except Exception:
            pass
    
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
    if (st.session_state.show_client_login or 
        st.session_state.show_client_registration or 
        st.session_state.show_password_reset):
        render_auth_forms()
        return
    
    # Маршрутизация по ролям
    if st.session_state.admin_logged_in:
        render_admin_panel()
    elif st.session_state.client_logged_in:
        render_client_cabinet()
    else:
        render_public_booking()

    # Глобальный футер с документами
    render_footer()

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