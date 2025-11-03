import streamlit as st
import time
from datetime import datetime, timedelta
from config.constants import BOOKING_RULES
from services.booking_service import BookingService
from services.client_service import ClientService
from services.notification_service import NotificationService
from ui.components import render_info_panel
from utils.validators import validate_phone, validate_email
from utils.product_cache import get_product_map
from utils.first_session_cache import has_paid_first_consultation_cached
from utils.docs import render_consent_line
from utils.datetime_helpers import now_msk

def render_public_booking():
    """Отрисовка публичной страницы записи с мобильной оптимизацией"""
    
    # Инициализация состояния шагов
    if 'booking_step' not in st.session_state:
        st.session_state.booking_step = 1
    if 'booking_form_data' not in st.session_state:
        st.session_state.booking_form_data = {}
    
    booking_service = BookingService()
    client_service = ClientService()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_booking_steps(booking_service, client_service)
    
    with col2:
        render_info_panel()

def render_booking_steps(booking_service, client_service):
    """Отрисовка пошаговой формы с мобильной навигацией"""
    current_step = st.session_state.booking_step
    
    # Индикатор прогресса с якорем для прокрутки
    st.markdown(f'<div id="step-indicator-{current_step}"></div>', unsafe_allow_html=True)
    render_progress_indicator(current_step)
    
    st.markdown("---")
    
    # Отрисовка текущего шага
    if current_step == 1:
        render_step_datetime(booking_service)
    elif current_step == 2:
        render_step_user_data()
    elif current_step == 3:
        render_step_confirmation(booking_service)
    elif current_step == 4:
        render_step_authorization(booking_service, client_service)
    
    # Скрипт для автоматической прокрутки к текущему шагу
    st.markdown(f"""
    <script>
        // Прокрутка к индикатору текущего шага
        setTimeout(function() {{
            const element = document.getElementById('step-indicator-{current_step}');
            if (element) {{
                element.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }}
        }}, 100);
        
        // Прокрутка к активному полю ввода при фокусе
        document.addEventListener('DOMContentLoaded', function() {{
            const inputs = document.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {{
                input.addEventListener('focus', function() {{
                    setTimeout(() => {{
                        this.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    }}, 300);
                }});
            }});
        }});
    </script>
    """, unsafe_allow_html=True)

def render_progress_indicator(current_step):
    """Визуальный индикатор прогресса"""
    steps = [
        {"num": 1, "icon": "📅", "title": "Дата и время"},
        {"num": 2, "icon": "👤", "title": "Ваши данные"},
        {"num": 3, "icon": "✅", "title": "Подтверждение"},
        {"num": 4, "icon": "🔐", "title": "Авторизация"}
    ]
    
    # Мобильная адаптация: компактное отображение на узких экранах
    st.markdown("""
    <style>
    /* Десктопная версия - полноценные карточки */
    .progress-desktop {
        display: flex !important;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .progress-desktop .step-card {
        flex: 1;
        text-align: center;
        padding: 15px;
        border-radius: 12px;
        transition: transform 0.2s;
    }

    /* Карточки могут рендериться вне контейнера .progress-desktop (Streamlit columns),
       поэтому даём отдельный селектор для самой карточки */
    .progress-desktop-card {
        display: block;
    }
    
    .progress-desktop .step-card.completed {
        background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%);
        color: white;
        box-shadow: 0 2px 8px rgba(136, 200, 188, 0.3);
    }
    
    .progress-desktop .step-card.active {
        background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(136, 200, 188, 0.4);
        border: 3px solid rgba(255, 255, 255, 0.5);
    }
    
    .progress-desktop .step-card.pending {
        background: rgba(240, 242, 245, 0.5);
        color: #9ca3af;
        border: 2px dashed rgba(156, 163, 175, 0.3);
    }
    
    /* Мобильная версия - компактная линия прогресса */
    .progress-mobile {
        display: none !important;
    }
    
    @media (max-width: 768px) {
        /* Скрываем десктопную версию */
        .progress-desktop {
            display: none !important;
        }
        
        /* Показываем мобильную версию */
        .progress-mobile {
            display: block !important;
            margin-bottom: 1.5rem;
        }
        
        /* Линия прогресса */
        .progress-bar-container {
            background: rgba(240, 242, 245, 0.8);
            height: 6px;
            border-radius: 10px;
            margin-bottom: 0.75rem;
            overflow: hidden;
        }
        
        .progress-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #88c8bc 0%, #6ba292 100%);
            border-radius: 10px;
            transition: width 0.4s ease;
        }
        
        /* Текущий шаг */
        .mobile-step-info {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.75rem 1rem;
            background: rgba(136, 200, 188, 0.1);
            border-radius: 10px;
            border-left: 3px solid #88c8bc;
        }
        
        .mobile-step-title {
            font-size: 0.95rem;
            font-weight: 600;
            color: #2d5a4f;
        }
        
        .mobile-step-counter {
            font-size: 0.85rem;
            color: #6ba292;
            font-weight: 500;
        }
        
        .mobile-step-icon {
            font-size: 1.5rem;
            margin-right: 0.5rem;
        }
        /* Скрываем карточки, которые могут быть отрендерены вне контейнера */
        .progress-desktop-card {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    # JavaScript: на клиенте принудительно переключаем видимость по ширине окна
    # Устанавливаем inline-стили с !important, чтобы переопределить любые внешние правила
    st.markdown("""
    <script>
    (function(){
        function collapseParents(el, levels){
            var p = el.parentElement;
            var i = 0;
            while(p && i < levels){
                try{
                    p.style.cssText = 'display: none !important; visibility: hidden !important; height: 0 !important; margin: 0 !important; padding: 0 !important; overflow: hidden !important;';
                }catch(e){}
                p = p.parentElement;
                i++;
            }
        }

        function restoreParents(el, levels){
            var p = el.parentElement;
            var i = 0;
            while(p && i < levels){
                try{
                    p.style.cssText = '';
                }catch(e){}
                p = p.parentElement;
                i++;
            }
        }

        function updateProgressView(){
            try{
                var desktops = Array.from(document.querySelectorAll('.progress-desktop'));
                var mobiles = Array.from(document.querySelectorAll('.progress-mobile'));
                if(desktops.length === 0 && mobiles.length === 0) return;
                if(window.innerWidth <= 768){
                    desktops.forEach(function(d){
                        d.style.cssText = 'display: none !important; visibility: hidden !important; height: 0 !important; margin: 0 !important; padding: 0 !important; overflow: hidden !important;';
                        // collapse a few parent levels to remove leftover whitespace
                        collapseParents(d, 3);
                    });
                    mobiles.forEach(function(m){ m.style.cssText = 'display: block !important;'; });
                } else {
                    desktops.forEach(function(d){
                        d.style.cssText = 'display: flex !important; visibility: visible !important; height: auto !important; margin: initial !important; padding: initial !important;';
                        restoreParents(d, 3);
                    });
                    mobiles.forEach(function(m){ m.style.cssText = 'display: none !important;'; });
                }
            }catch(e){console.error(e)}
        }

        window.addEventListener('load', updateProgressView);
        window.addEventListener('resize', function(){ setTimeout(updateProgressView, 100); });
        setTimeout(updateProgressView, 50);
    })();
    </script>
    """, unsafe_allow_html=True)
    
    # Вычисляем процент прогресса
    progress_percent = (current_step / len(steps)) * 100
    
    # Мобильная версия - компактная линия прогресса
    st.markdown(f"""
    <div class="progress-mobile">
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {progress_percent}%"></div>
        </div>
        <div class="mobile-step-info">
            <div style="display: flex; align-items: center;">
                <span class="mobile-step-icon">{steps[current_step-1]["icon"]}</span>
                <span class="mobile-step-title">{steps[current_step-1]["title"]}</span>
            </div>
            <span class="mobile-step-counter">Шаг {current_step} из {len(steps)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ОТКРЫВАЕМ контейнер для десктопной версии
    st.markdown('<div class="progress-desktop">', unsafe_allow_html=True)
    
    cols = st.columns(4)
    
    for idx, step in enumerate(steps):
        with cols[idx]:
            if step["num"] < current_step:
                # Завершенный шаг
                st.markdown(f"""
             <div class="step-card progress-desktop-card" style="text-align: center; padding: 15px; background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%); 
                 border-radius: 12px; color: white; box-shadow: 0 2px 8px rgba(136, 200, 188, 0.3);">
                    <div style="font-size: 28px; margin-bottom: 5px;">✓</div>
                    <div style="font-size: 12px; font-weight: 600;">{step["title"]}</div>
                </div>
                """, unsafe_allow_html=True)
            elif step["num"] == current_step:
                # Текущий шаг с якорем для прокрутки
                st.markdown(f"""
             <div id="current-step" class="step-card progress-desktop-card" style="text-align: center; padding: 15px; background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%); 
                 border-radius: 12px; color: white; box-shadow: 0 4px 12px rgba(136, 200, 188, 0.4);
                 border: 3px solid rgba(255, 255, 255, 0.5);">
                    <div style="font-size: 28px; margin-bottom: 5px;">{step["icon"]}</div>
                    <div style="font-size: 12px; font-weight: 700;">{step["title"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Будущий шаг
                st.markdown(f"""
             <div class="step-card progress-desktop-card" style="text-align: center; padding: 15px; background: rgba(240, 242, 245, 0.5); 
                 border-radius: 12px; color: #9ca3af; border: 2px dashed rgba(156, 163, 175, 0.3);">
                    <div style="font-size: 28px; margin-bottom: 5px; opacity: 0.5;">{step["icon"]}</div>
                    <div style="font-size: 12px; font-weight: 500;">{step["title"]}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # ЗАКРЫВАЕМ контейнер для десктопной версии (ВНЕ цикла)
    st.markdown('</div>', unsafe_allow_html=True)

def render_step_datetime(booking_service):
    """Шаг 1: Выбор даты и времени с якорями"""
    st.markdown('<div id="step1-form"></div>', unsafe_allow_html=True)
    st.markdown("### 📅 Шаг 1: Выберите дату и время")
    st.caption("Всё время — по Москве (MSK)")
    
    # Выбор даты
    min_date = now_msk().date()
    max_date = min_date + timedelta(days=BOOKING_RULES["MAX_DAYS_AHEAD"])
    
    st.markdown('<div id="date-picker"></div>', unsafe_allow_html=True)
    selected_date = st.date_input(
        "Дата консультации", 
        min_value=min_date,
        max_value=max_date, 
        value=st.session_state.booking_form_data.get('date', min_date),
        format="DD.MM.YYYY",
        key="step1_date"
    )
    
    # Получаем доступные слоты
    available_slots = booking_service.get_available_slots(str(selected_date))
    
    if not available_slots:
        st.warning("😔 На выбранную дату нет свободных слотов. Выберите другую дату.")
        return
    
    st.markdown('<div id="time-slots"></div>', unsafe_allow_html=True)
    st.markdown("#### 🕐 Доступные временные слоты")
    st.info(f"💡 Доступно {len(available_slots)} слотов на {selected_date.strftime('%d.%m.%Y')}")
    
    # Отображение слотов в сетке
    cols = st.columns(4)
    selected_time = st.session_state.booking_form_data.get('time')
    
    for idx, time_slot in enumerate(available_slots):
        with cols[idx % 4]:
            is_selected = (time_slot == selected_time)
            button_type = "primary" if is_selected else "secondary"
            label = f"{'✓ ' if is_selected else ''}🕐 {time_slot}"
            if st.button(label, key=f"slot_{time_slot}", use_container_width=True, type=button_type):
                with st.spinner("⏳ Загружаем выбранное время..."):
                    time.sleep(0.2)
                    st.session_state.booking_form_data['date'] = selected_date
                    st.session_state.booking_form_data['time'] = time_slot
                    st.rerun()
    
    # Кнопки навигации
    st.markdown("---")
    st.markdown('<div id="step1-nav"></div>', unsafe_allow_html=True)
    col_nav1, col_nav2 = st.columns([1, 1])
    
    with col_nav2:
        if selected_time:
            if st.button("Далее ➡️", use_container_width=True, type="primary", key="step1_next"):
                with st.spinner("🚪 Переходим на следующий шаг..."):
                    time.sleep(0.2)
                st.session_state.booking_step = 2
                st.rerun()
        else:
            st.button("Выберите время", use_container_width=True, disabled=True)

def render_step_user_data():
    """Шаг 2: Заполнение данных с якорями для каждого поля"""
    st.markdown('<div id="step2-form"></div>', unsafe_allow_html=True)
    st.markdown("### 👤 Шаг 2: Ваши данные")
    
    form_data = st.session_state.booking_form_data
    
    # Показываем выбранные дату и время
    if form_data.get('date') and form_data.get('time'):
        st.success(f"✅ Выбрано: **{form_data['date'].strftime('%d.%m.%Y')}** в **{form_data['time']}**")
    
    st.markdown("---")
    
    # Форма данных с якорями для мобильной прокрутки
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown('<div id="field-name"></div>', unsafe_allow_html=True)
        client_name = st.text_input(
            "👤 Ваше имя *", 
            placeholder="Иван Иванов",
            value=form_data.get('name', ''),
            key="step2_name"
        )
        
        st.markdown('<div id="field-email"></div>', unsafe_allow_html=True)
        client_email = st.text_input(
            "📧 Email", 
            placeholder="example@mail.com",
            value=form_data.get('email', ''),
            key="step2_email"
        )
        
        st.info("Если хотите получать уведомления в Telegram, подключите бота позже в личном кабинете в разделе 'Уведомления'")
    
    with col_b:
        st.markdown('<div id="field-phone"></div>', unsafe_allow_html=True)
        client_phone = st.text_input(
            "📱 Телефон *",
            placeholder="+7XXXXXXXXXX",
            value=form_data.get('phone', ''),
            key="step2_phone"
        )
        st.markdown('<div id="field-telegram"></div>', unsafe_allow_html=True)
        client_telegram = st.text_input(
            "💬 Telegram username",
            placeholder="@username",
            value=form_data.get('telegram', ''),
            key="step2_telegram"
        )
    
    st.markdown('<div id="field-notes"></div>', unsafe_allow_html=True)
    notes = st.text_area(
        "💭 Тема консультации (необязательно)", 
        height=80,
        value=form_data.get('notes', ''),
        placeholder="Опишите, что вас беспокоит или какой вопрос хотите обсудить...",
        key="step2_notes"
    )
    
    # Кнопки навигации
    st.markdown("---")
    st.markdown('<div id="step2-nav"></div>', unsafe_allow_html=True)
    col_nav1, col_nav2 = st.columns([1, 1])
    
    with col_nav1:
        if st.button("⬅️ Назад", use_container_width=True, key="step2_back"):
            with st.spinner("Пожалуйста, подождите..."):
                time.sleep(0.2)
                st.session_state.booking_step = 1
                st.rerun()
    
    with col_nav2:
        if st.button("Далее ➡️", use_container_width=True, type="primary", key="step2_next"):
            with st.spinner("Пожалуйста, подождите..."):
                time.sleep(0.2)
                # Валидация и переход
                client_name_clean = client_name.strip() if isinstance(client_name, str) else client_name
                client_phone_clean = client_phone.strip() if isinstance(client_phone, str) else client_phone
                client_email_clean = client_email.strip() if isinstance(client_email, str) else client_email
                client_telegram_clean = client_telegram.strip() if isinstance(client_telegram, str) else client_telegram
                notes_clean = notes.strip() if isinstance(notes, str) else notes
                
                if not client_name_clean or not client_phone_clean:
                    st.error("❌ Заполните имя и телефон")
                else:
                    phone_valid, phone_msg = validate_phone(client_phone_clean)
                    if not phone_valid:
                        st.error(phone_msg)
                    else:
                        if client_email_clean:
                            email_valid, email_msg = validate_email(client_email_clean)
                            if not email_valid:
                                st.error(email_msg)
                                return
                        
                        st.session_state.booking_form_data.update({
                            'name': client_name_clean,
                            'phone': client_phone_clean,
                            'email': client_email_clean,
                            'telegram': client_telegram_clean,
                            'notes': notes_clean
                        })
                        st.session_state.booking_step = 3
                        st.rerun()

def render_step_confirmation(booking_service):
    """Шаг 3: Подтверждение с прокруткой к кнопке"""
    st.markdown('<div id="step3-form"></div>', unsafe_allow_html=True)
    st.markdown("### ✅ Шаг 3: Подтверждение заказа")
    
    form_data = st.session_state.booking_form_data
    
    # Получаем продукт по умолчанию
    try:
        from core.database import db_manager
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
    
    st.markdown("#### 📋 Детали записи")
    
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

def render_step_authorization(booking_service, client_service):
    """Шаг 4: Авторизация с якорями для вкладок"""
    st.markdown('<div id="step4-form"></div>', unsafe_allow_html=True)
    st.markdown("### 🔐 Шаг 4: Авторизация")
    
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
    st.markdown("#### Выберите действие:")
    
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

# Остальные функции (render_login_tab, render_registration_tab, render_pay_later_tab) 
# остаются без изменений из исходного файла

def render_login_tab(form_data, client_service):
    """Вкладка входа"""
    st.markdown("##### Войдите в существующий аккаунт")
    
    with st.form("step4_login"):
        login_phone = st.text_input(
            "📱 Номер телефона", 
            placeholder="+7 (999) 123-45-67",
            value=form_data.get('phone', '')
        )
        login_password = st.text_input("🔑 Пароль", type="password")
        
        submitted = st.form_submit_button("🔐 Войти и перейти к оплате", use_container_width=True)
        
        if submitted:
            if not login_phone or not login_password:
                st.error("❌ Заполните все поля")
            else:
                # Обрезаем пробелы у номера
                login_phone_clean = login_phone.strip() if isinstance(login_phone, str) else login_phone
                from core.auth import AuthManager
                auth_manager = AuthManager()
                
                if auth_manager.verify_client_password(login_phone_clean, login_password):
                    # Получаем информацию о клиенте
                    profile = client_service.get_profile(login_phone_clean)
                    client_info = profile or client_service.get_client_info(login_phone_clean)
                    
                    if client_info:
                        # Авторизуем
                        st.session_state.client_logged_in = True
                        st.session_state.client_phone = login_phone_clean
                        st.session_state.client_name = client_info['client_name']
                        st.session_state.client_nav = "👁️ Мои ближайшие консультации"
                        
                        # Remember me token
                        try:
                            token = auth_manager.issue_remember_token(login_phone_clean)
                            if token:
                                st.query_params["rt"] = token
                        except Exception:
                            pass
                        
                        # Очищаем форму
                        st.session_state.booking_step = 1
                        st.session_state.booking_form_data = {}
                        
                        st.success("✅ Вход выполнен! Перенаправляем в личный кабинет...")
                        st.rerun()
                    else:
                        st.error("❌ Клиент не найден")
                else:
                    st.error("❌ Неверный номер телефона или пароль")

def render_registration_tab(form_data, client_service):
    """Вкладка регистрации"""
    st.markdown("##### Создайте новый аккаунт")
    st.info("💡 Регистрация позволит управлять записями и получать уведомления")
    
    with st.form("step4_registration"):
        reg_name = st.text_input("👤 Имя", value=form_data.get('name', ''))
        reg_phone = st.text_input("📱 Телефон", value=form_data.get('phone', ''))
        reg_email = st.text_input("📧 Email", value=form_data.get('email', ''))
        
        col_pass1, col_pass2 = st.columns(2)
        with col_pass1:
            reg_password = st.text_input("🔑 Придумайте пароль", type="password", help="Минимум 6 символов")
        with col_pass2:
            reg_confirm = st.text_input("🔑 Подтвердите пароль", type="password")
        
        submitted = st.form_submit_button("📝 Зарегистрироваться и перейти к оплате", use_container_width=True)
        
        if submitted:
            # Обрезаем пробелы у полей (кроме пароля)
            reg_name_clean = reg_name.strip() if isinstance(reg_name, str) else reg_name
            reg_phone_clean = reg_phone.strip() if isinstance(reg_phone, str) else reg_phone
            reg_email_clean = reg_email.strip() if isinstance(reg_email, str) else reg_email

            if not reg_name_clean or not reg_phone_clean or not reg_password:
                st.error("❌ Заполните все обязательные поля")
            elif reg_password != reg_confirm:
                st.error("❌ Пароли не совпадают")
            elif len(reg_password) < 6:
                st.error("❌ Пароль должен быть не менее 6 символов")
            else:
                from core.auth import AuthManager
                from utils.validators import validate_phone, validate_email
                
                phone_valid, phone_msg = validate_phone(reg_phone_clean)
                if not phone_valid:
                    st.error(phone_msg)
                    return
                
                if reg_email_clean:
                    email_valid, email_msg = validate_email(reg_email_clean)
                    if not email_valid:
                        st.error(email_msg)
                        return
                
                auth_manager = AuthManager()
                
                # Создаем аккаунт
                if auth_manager.create_client_password(reg_phone_clean, reg_password):
                    # Сохраняем профиль
                    try:
                        client_service.upsert_profile(
                            reg_phone_clean, 
                            reg_name_clean, 
                            reg_email_clean, 
                            form_data.get('telegram', '').strip()
                        )
                    except Exception:
                        pass
                    
                    # Авторизуем
                    st.session_state.client_logged_in = True
                    st.session_state.client_phone = reg_phone_clean
                    st.session_state.client_name = reg_name_clean
                    st.session_state.client_nav = "👁️ Мои ближайшие консультации"
                    
                    # Remember me token
                    try:
                        token = auth_manager.issue_remember_token(reg_phone_clean)
                        if token:
                            st.query_params["rt"] = token
                    except Exception:
                        pass
                    
                    # Очищаем форму
                    st.session_state.booking_step = 1
                    st.session_state.booking_form_data = {}
                    
                    st.success("✅ Регистрация завершена! Перенаправляем в личный кабинет...")
                    st.rerun()
                else:
                    st.error("❌ Ошибка регистрации")

def render_pay_later_tab(form_data):
    """Вкладка отложенной оплаты"""
    st.markdown("##### Оплатить позже")
    
    st.warning("""
    ⚠️ **Важно:** Без авторизации вы не сможете управлять заказом
    
    Ваш заказ создан, но для доступа к нему и оплаты необходимо войти в личный кабинет.
    """)
    
    st.info("""
    📌 **Что делать дальше:**
    1. Вернитесь на главную страницу
    2. Войдите в личный кабинет через кнопку "🔐 Войти в кабинет" внизу страницы
    3. Найдите ваш заказ в разделе "Мои ближайшие консультации"
    4. Оплатите заказ
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🏠 На главную", use_container_width=True, type="primary"):
            with st.spinner("⏳ Возврат на главную..."):
                time.sleep(0.2)
                st.session_state.booking_step = 1
                st.session_state.booking_form_data = {}
                st.rerun()
    
    with col2:
        if st.button("🔐 Войти сейчас", use_container_width=True):
            with st.spinner("⏳ Открываем форму входа..."):
                time.sleep(0.2)
                st.session_state.show_client_login = True
                st.rerun()

    # Если пользователь нажал "Войти сейчас" — показываем форму входа прямо здесь
    if st.session_state.get("show_client_login"):
        st.markdown("---")
        st.markdown("#### Вход в личный кабинет")
        with st.form("pay_later_login_form"):
            login_phone = st.text_input(
                "📱 Номер телефона",
                placeholder="+7 (999) 123-45-67",
                key="pay_later_login_phone"
            )
            login_password = st.text_input("🔑 Пароль", type="password", key="pay_later_login_password")
            submitted = st.form_submit_button("🔐 Войти", use_container_width=True)
            if submitted:
                if not login_phone or not login_password:
                    st.error("❌ Заполните все поля")
                else:
                    login_phone_clean = login_phone.strip() if isinstance(login_phone, str) else login_phone
                    from core.auth import AuthManager
                    auth_manager = AuthManager()
                    if auth_manager.verify_client_password(login_phone_clean, login_password):
                        from services.client_service import ClientService
                        client_service = ClientService()
                        profile = client_service.get_profile(login_phone_clean)
                        client_info = profile or client_service.get_client_info(login_phone_clean)
                        if client_info:
                            st.session_state.client_logged_in = True
                            st.session_state.client_phone = login_phone_clean
                            st.session_state.client_name = client_info['client_name']
                            st.session_state.client_nav = "👁️ Мои ближайшие консультации"
                            try:
                                token = auth_manager.issue_remember_token(login_phone_clean)
                                if token:
                                    st.query_params["rt"] = token
                            except Exception:
                                pass
                            st.success("✅ Вход выполнен! Перенаправляем...")
                            st.session_state.show_client_login = False
                            st.rerun()
                        else:
                            st.error("❌ Не удалось найти профиль клиента")
                    else:
                        st.error("❌ Неверный номер телефона или пароль")