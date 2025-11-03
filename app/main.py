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

def render_top_bar():
    """Компактная верхняя панель с навигацией"""
    
    # Разделяем на логотип/название и действия
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("## 🌿 Запись на онлайн-консультацию")
    
    with col2:
        # Для клиента
        if st.session_state.client_logged_in:
            st.markdown(f"**👤 {st.session_state.client_name}**")
            
            # Статус Telegram
            from services.notification_service import NotificationService
            notification_service = NotificationService()
            telegram_connected = notification_service.get_client_telegram_chat_id(st.session_state.client_phone)
            
            col_a, col_b = st.columns(2)
            with col_a:
                if telegram_connected:
                    st.success("🔔 Уведомления")
                else:
                    st.warning("🔕 Без уведомлений")
            
            with col_b:
                if st.button("🚪 Выйти", use_container_width=True, key="client_logout_top"):
                    try:
                        auth = AuthManager()
                        if st.session_state.client_phone:
                            auth.revoke_tokens(st.session_state.client_phone)
                        st.query_params.clear()
                    except Exception:
                        pass
                    from core.session_state import client_logout
                    client_logout()
                    st.rerun()
        
        # Для администратора
        elif st.session_state.admin_logged_in:
            st.success("**👩‍💼 Здравствуйте, Анна**")
            
            # Быстрая статистика
            from services.analytics_service import AnalyticsService
            analytics_service = AnalyticsService()
            total, upcoming, this_month, this_week = analytics_service.get_stats()
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("Всего", total, label_visibility="collapsed")
                st.caption("📋 Всего")
            with col_stat2:
                st.metric("Предстоящих", upcoming, label_visibility="collapsed")
                st.caption("⏰ Предстоящих")
            with col_stat3:
                if st.button("🚪 Выйти", use_container_width=True, key="admin_logout_top"):
                    from core.session_state import admin_logout
                    try:
                        auth = AuthManager()
                        auth.revoke_admin_tokens()
                        _pop_query_param('at')
                    except Exception:
                        pass
                    admin_logout()
                    st.rerun()
        
        # Для гостей
        else:
            col_auth1, col_auth2 = st.columns(2)
            with col_auth1:
                if st.button("🔐 Войти", use_container_width=True, key="guest_login_top"):
                    st.session_state.show_client_login = True
                    st.session_state.show_client_registration = False
                    st.session_state.show_password_reset = False
                    st.rerun()
            
            with col_auth2:
                if st.button("📝 Регистрация", use_container_width=True, key="guest_register_top"):
                    st.session_state.show_client_login = False
                    st.session_state.show_client_registration = True
                    st.session_state.show_password_reset = False
                    st.rerun()
    
    st.markdown("---")

def render_admin_login_modal():
    """Модальное окно для входа администратора"""
    if st.session_state.get('show_admin_login_modal'):
        with st.container():
            st.markdown("### 👩‍💼 Вход для администратора")
            
            with st.form("admin_login_form_modal", clear_on_submit=True):
                password = st.text_input("Пароль администратора", type="password", key="admin_pass_modal")
                
                col_submit, col_cancel = st.columns([1, 1])
                with col_submit:
                    submit = st.form_submit_button("Войти", use_container_width=True)
                with col_cancel:
                    if st.form_submit_button("Отмена", use_container_width=True):
                        st.session_state.show_admin_login_modal = False
                        st.rerun()
                
                if submit:
                    auth_manager = AuthManager()
                    if password and auth_manager.check_admin_password(password):
                        from core.session_state import admin_login
                        admin_login()
                        st.success("✅ Добро пожаловать!")
                        try:
                            at = auth_manager.issue_admin_token()
                            if at:
                                _set_query_param("at", at)
                        except Exception:
                            pass
                        st.session_state.show_admin_login_modal = False
                        st.rerun()
                    elif password:
                        st.error("❌ Неверный пароль!")
            
            st.markdown("---")

def render_footer():
    """Футер с документами и ссылкой на вход администратора"""
    st.markdown("---")
    
    col_footer1, col_footer2 = st.columns([3, 1])
    
    with col_footer1:
        try:
            from core.database import db_manager
            sb = db_manager.get_client()
            policy_url = None
            offer_url = None
            if sb is not None:
                resp = sb.table('documents').select('doc_type, url, is_active, updated_at')\
                    .eq('is_active', True).execute()
                rows = resp.data or []
                for doc_type in ('policy', 'offer'):
                    docs = [r for r in rows if (r.get('doc_type') == doc_type and r.get('url'))]
                    docs.sort(key=lambda r: r.get('updated_at') or '', reverse=True)
                    if docs:
                        if doc_type == 'policy':
                            policy_url = docs[0]['url']
                        else:
                            offer_url = docs[0]['url']
            
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
            pass
    
    with col_footer2:
        # Кнопка входа администратора только для гостей
        if not st.session_state.client_logged_in and not st.session_state.admin_logged_in:
            if st.button("👩‍💼 Для администратора", use_container_width=True, key="admin_link_footer"):
                st.session_state.show_admin_login_footer = True
                st.rerun()
            # Показываем форму для пароля прямо под кнопкой
            if st.session_state.get('show_admin_login_footer'):
                st.markdown("### 👩‍💼 Вход для администратора")
                with st.form("admin_login_form_footer", clear_on_submit=True):
                    password = st.text_input("Пароль администратора", type="password", key="admin_pass_footer")
                    col_submit, col_cancel = st.columns([1, 1])
                    with col_submit:
                        submit = st.form_submit_button("Войти", use_container_width=True)
                    with col_cancel:
                        if st.form_submit_button("Отмена", use_container_width=True):
                            st.session_state.show_admin_login_footer = False
                            st.rerun()
                    if submit:
                        auth_manager = AuthManager()
                        if password and auth_manager.check_admin_password(password):
                            from core.session_state import admin_login
                            admin_login()
                            st.success("✅ Добро пожаловать!")
                            try:
                                at = auth_manager.issue_admin_token()
                                if at:
                                    _set_query_param("at", at)
                            except Exception:
                                pass
                            st.session_state.show_admin_login_footer = False
                            st.rerun()
                        elif password:
                            st.error("❌ Неверный пароль!")

def main():
    """Главная функция приложения"""
    # Инициализация приложения
    page_config = config.PAGE_CONFIG.copy()
    page_config["initial_sidebar_state"] = "collapsed"  # Скрываем сайдбар
    st.set_page_config(**page_config)
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
                    from services.client_service import ClientService
                    cs = ClientService()
                    info = cs.get_client_info(phone_norm)
                    st.session_state.client_logged_in = True
                    st.session_state.client_phone = phone_norm
                    st.session_state.client_name = (info['client_name'] if info else st.session_state.get('client_name', ''))
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
    
    # Верхняя панель
    render_top_bar()
    
    # Модальное окно входа администратора
    if st.session_state.get('show_admin_login_modal'):
        render_admin_login_modal()
    
    # Отображение форм аутентификации если нужно
    if (st.session_state.show_client_login or 
        st.session_state.show_client_registration or 
        st.session_state.show_password_reset):
        render_auth_forms()
    else:
        # Маршрутизация по ролям
        if st.session_state.admin_logged_in:
            render_admin_panel()
        elif st.session_state.client_logged_in:
            render_client_cabinet()
        else:
            render_public_booking()
    
    # Футер
    render_footer()

if __name__ == "__main__":
    main()