import streamlit as st
import time
from utils.docs import render_consent_line
from core.database import db_manager

def render_step_confirmation(booking_service):
    """Шаг 3: Подтверждение с прокруткой к кнопке"""
    st.markdown('<div id="step3-form"></div>', unsafe_allow_html=True)
    st.markdown("""
             <h2 style="color: #225c52; font-size: 1.4rem; font-weight: 600; 
                  margin-bottom: 1.4rem; padding-bottom: 0.75rem; 
                  border-bottom: 2px solid rgba(136, 200, 188, 0.2);">
                 ✅ Шаг 3: Подтверждение заказа
             </h2>
    """, unsafe_allow_html=True)
    
    form_data = st.session_state.booking_form_data
    
    # Получаем продукт по умолчанию
    try:
        supabase = db_manager.get_client()
        products_all = supabase.table('products').select('id,name,price_rub,is_featured,is_active').eq('is_active', True).order('sort_order').execute().data or []
    except Exception:
        products_all = []
    
    featured = [p for p in products_all if p.get('is_featured')]
    chosen = (featured[0] if featured else (products_all[0] if products_all else None))
    
    # Карточка подтверждения
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.95); padding: 25px; border-radius: 16px; 
         border: 1px solid rgba(136, 200, 188, 0.25); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);">
    """, unsafe_allow_html=True)
    
    st.markdown("""
             <h2 style="color: #225c52; font-size: 1.25rem; font-weight: 600; 
                  margin-bottom: 1.25rem; padding-bottom: 0.75rem; 
                  border-bottom: 2px solid rgba(136, 200, 188, 0.2);">
                 📋 Детали записи
             </h2>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📅 Дата и время:**")
        st.info(f"🗓️ {form_data.get('date').strftime('%d.%m.%Y')}\n\n🕐 {form_data.get('time')}")
        
        st.markdown("**👤 Ваши данные:**")
        st.write(f"**Имя:** {form_data.get('name')}")
        st.write(f"**Телефон:** {form_data.get('phone')}")
        if form_data.get('email'):
            st.write(f"**Email:** {form_data.get('email')}")
        if form_data.get('telegram'):
            st.write(f"**Telegram:** {form_data.get('telegram')}")
    
    with col2:
        if chosen:
            st.markdown("**💳 Продукт:**")
            st.success(f"""
            **{chosen.get('name')}**
            
            💰 Стоимость: **{chosen.get('price_rub')} ₽**
            """)
        
        if form_data.get('notes'):
            st.markdown("**💭 Тема консультации:**")
            st.info(form_data.get('notes'))
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Согласие с условиями
    st.markdown("---")
    render_consent_line()
    
    # Кнопки навигации с якорем
    st.markdown("---")
    st.markdown('<div id="step3-nav"></div>', unsafe_allow_html=True)
    col_nav1, col_nav2 = st.columns([1, 1])
    
    with col_nav1:
        if st.button("⬅️ Назад", use_container_width=True, key="step3_back"):
            with st.spinner("Пожалуйста, подождите..."):
                time.sleep(0.2)
                st.session_state.booking_step = 2
                st.rerun()
    
    with col_nav2:
        if st.button("✅ Создать заказ", use_container_width=True, type="primary", key="step3_confirm"):
            with st.spinner("Создаём заказ..."):
                time.sleep(0.2)
                booking_data = {
                    'client_name': form_data.get('name'),
                    'client_phone': form_data.get('phone'),
                    'client_email': form_data.get('email', ''),
                    'client_telegram': form_data.get('telegram', ''),
                    'booking_date': str(form_data.get('date')),
                    'booking_time': form_data.get('time'),
                    'notes': form_data.get('notes', ''),
                    'telegram_chat_id': form_data.get('chat_id', ''),
                    'status': 'pending_payment'
                }
                
                success, message = booking_service.create_booking(booking_data)
                
                if success:
                    st.session_state.booking_form_data['booking_created'] = True
                    
                    if chosen:
                        try:
                            row = booking_service.get_booking_by_datetime(
                                form_data.get('phone'),
                                str(form_data.get('date')),
                                form_data.get('time')
                            )
                            if row:
                                booking_service.set_booking_payment_info(
                                    row['id'], 
                                    chosen.get('id'), 
                                    float(chosen.get('price_rub') or 0)
                                )
                                st.session_state.booking_form_data['booking_id'] = row['id']
                        except Exception:
                            pass
                    
                    st.balloons()
                    st.success("✅ Заказ успешно создан!")
                    st.session_state.booking_step = 4
                    st.rerun()
                else:
                    st.error(message)