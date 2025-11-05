import streamlit as st
import time
from .auth_components import render_login_tab, render_registration_tab, render_pay_later_tab

def render_step_authorization(booking_service, client_service):
    """Шаг 4: Авторизация с якорями для вкладок"""
    st.markdown('<div id="step4-form"></div>', unsafe_allow_html=True)
    st.markdown("""
             <h2 style="color: #225c52; font-size: 1.4rem; font-weight: 600; 
                  margin-bottom: 1.4rem; padding-bottom: 0.75rem; 
                  border-bottom: 2px solid rgba(136, 200, 188, 0.2);">
                 🔐 Шаг 4: Авторизация
             </h2>
    """, unsafe_allow_html=True)
    
    form_data = st.session_state.booking_form_data
    
    st.success("🎉 Ваш заказ успешно создан!")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(255, 243, 224, 0.95) 0%, rgba(255, 224, 178, 0.95) 100%); 
         padding: 20px; border-radius: 12px; border-left: 4px solid #ff9800; margin: 20px 0;">
        <h4 style="margin: 0 0 10px 0; color: #e65100;">⏳ Заказ ожидает оплаты</h4>
        <p style="margin: 0; color: #5d4037;">
            Для завершения записи войдите в личный кабинет и перейдите к оплате.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
             <h2 style="color: #225c52; font-size: 1.25rem; font-weight: 600; 
                  margin-bottom: 1.25rem; padding-bottom: 0.75rem; 
                  border-bottom: 2px solid rgba(136, 200, 188, 0.2);">
                 Выберите действие:
             </h2>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 Войти", "📝 Регистрация", "💳 Оплатить позже"])
    
    with tab1:
        st.markdown('<div id="login-tab"></div>', unsafe_allow_html=True)
        render_login_tab(form_data, client_service)
    
    with tab2:
        st.markdown('<div id="register-tab"></div>', unsafe_allow_html=True)
        render_registration_tab(form_data, client_service)
    
    with tab3:
        st.markdown('<div id="later-tab"></div>', unsafe_allow_html=True)
        render_pay_later_tab(form_data)