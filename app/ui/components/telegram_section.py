import streamlit as st
from services.notification_service import NotificationService
from services.booking_service import BookingService
from utils.validators import normalize_phone, hash_password

def render_telegram_section():
    """Интуитивная секция подключения Telegram с пошаговой инструкцией"""
    st.markdown("### 💬 Уведомления в Telegram")
    
    notification_service = NotificationService()
    booking_service = BookingService()
    
    # Получаем текущий chat_id клиента
    current_chat_id = notification_service.get_client_telegram_chat_id(st.session_state.client_phone)
    
    if current_chat_id:
        render_connected_state(notification_service, booking_service, current_chat_id)
    else:
        render_connection_wizard(notification_service)

def render_connected_state(notification_service, booking_service, chat_id):
    """Отображение для подключенного состояния"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(227, 242, 253, 0.95) 0%, rgba(187, 222, 251, 0.95) 100%); 
         padding: 25px; border-radius: 16px; border-left: 5px solid #0088cc; 
         box-shadow: 0 4px 12px rgba(0, 136, 204, 0.15); margin-bottom: 25px;">
        <h3 style="margin: 0 0 15px 0; color: #0088cc; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 32px;">✅</span>
            <span>Telegram подключен!</span>
        </h3>
        <p style="margin: 0; color: #014361; font-size: 15px; line-height: 1.6;">
            Вы будете получать автоматические уведомления о всех важных событиях
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Что вы получаете
    st.markdown("#### 🎁 Что вы получаете:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 12px; 
             border: 1px solid rgba(136, 200, 188, 0.2); margin-bottom: 15px;
             box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);">
            <div style="font-size: 32px; margin-bottom: 10px;">✅</div>
            <div style="font-weight: 600; color: #2d3748; margin-bottom: 8px;">Подтверждения записей</div>
            <div style="color: #718096; font-size: 14px;">Мгновенное уведомление при создании новой записи</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 12px; 
             border: 1px solid rgba(136, 200, 188, 0.2); margin-bottom: 15px;
             box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);">
            <div style="font-size: 32px; margin-bottom: 10px;">⏰</div>
            <div style="font-weight: 600; color: #2d3748; margin-bottom: 8px;">Умные напоминания</div>
            <div style="color: #718096; font-size: 14px;">Автоматическое напоминание за 1 час до консультации</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 12px; 
             border: 1px solid rgba(136, 200, 188, 0.2); margin-bottom: 15px;
             box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);">
            <div style="font-size: 32px; margin-bottom: 10px;">💳</div>
            <div style="font-weight: 600; color: #2d3748; margin-bottom: 8px;">Статусы оплаты</div>
            <div style="color: #718096; font-size: 14px;">Уведомления об успешной оплате и изменениях</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 12px; 
             border: 1px solid rgba(136, 200, 188, 0.2); margin-bottom: 15px;
             box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);">
            <div style="font-size: 32px; margin-bottom: 10px;">❌</div>
            <div style="font-weight: 600; color: #2d3748; margin-bottom: 8px;">Отмены</div>
            <div style="color: #718096; font-size: 14px;">Моментальное уведомление об отмене записи</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Действия
    st.markdown("---")
    st.markdown("#### ⚙️ Управление")
    
    col_test, col_disable = st.columns([1, 1])
    
    with col_test:
        if st.button("📤 Отправить тестовое сообщение", use_container_width=True, type="primary"):
            if notification_service.bot.send_to_client(chat_id, "✅ <b>Тест успешен!</b>\n\nУведомления работают корректно. Вы будете получать все важные сообщения."):
                st.success("✅ Тестовое сообщение отправлено! Проверьте Telegram")
            else:
                st.error("❌ Не удалось отправить. Попробуйте переподключить")
    
    with col_disable:
        with st.popover("🔕 Отключить уведомления", use_container_width=True):
            st.warning("Вы перестанете получать напоминания и важные уведомления")
            if st.button("Подтвердить отключение", type="secondary", use_container_width=True):
                # Удаляем chat_id из всех записей клиента
                try:
                    from utils.validators import hash_password, normalize_phone
                    from core.database import db_manager
                    phone_hash = hash_password(normalize_phone(st.session_state.client_phone))
                    db_manager.get_client().table('bookings')\
                        .update({'telegram_chat_id': None})\
                        .eq('phone_hash', phone_hash)\
                        .execute()
                    st.success("✅ Уведомления отключены")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Ошибка: {e}")

def render_connection_wizard(notification_service):
    """Пошаговый визард подключения Telegram"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(255, 243, 224, 0.95) 0%, rgba(255, 224, 178, 0.95) 100%); 
         padding: 25px; border-radius: 16px; border-left: 5px solid #ff9800; 
         box-shadow: 0 4px 12px rgba(255, 152, 0, 0.15); margin-bottom: 25px;">
        <h3 style="margin: 0 0 10px 0; color: #e65100; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 32px;">⚠️</span>
            <span>Telegram не подключен</span>
        </h3>
        <p style="margin: 0; color: #5d4037; font-size: 15px;">
            Без Telegram вы не будете получать напоминания о консультациях
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🚀 Подключение за 2 простых шага")
    st.markdown("Следуйте инструкциям по порядку — это займёт всего 1 минуту")
    
    # Инициализация состояния
    if 'telegram_step_completed' not in st.session_state:
        st.session_state.telegram_step_completed = {1: False, 2: False}
    
    # ШАГ 1: Открыть бота
    render_step_1(notification_service)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ШАГ 2: Получить Chat ID
    render_step_2()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ШАГ 3: Ввести Chat ID
    render_step_3(notification_service)

def render_step_1(notification_service):
    """Шаг 1: Открыть бота"""
    is_completed = st.session_state.telegram_step_completed.get(1, False)
    
    border_color = "#88c8bc" if is_completed else "#e2e8f0"
    bg_color = "rgba(136, 200, 188, 0.05)" if is_completed else "white"
    
    st.markdown(f"""
    <div style="background: {bg_color}; padding: 25px; border-radius: 16px; 
         border: 2px solid {border_color}; margin-bottom: 20px;
         box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);">
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
            <div style="background: {'linear-gradient(135deg, #88c8bc 0%, #6ba292 100%)' if is_completed else '#e2e8f0'}; 
                 color: {'white' if is_completed else '#718096'}; 
                 width: 48px; height: 48px; border-radius: 50%; 
                 display: flex; align-items: center; justify-content: center; 
                 font-size: 24px; font-weight: bold; flex-shrink: 0;">
                {'✓' if is_completed else '1'}
            </div>
            <div>
                <h4 style="margin: 0; color: #2d3748; font-size: 20px;">Откройте нашего Telegram-бота</h4>
                <p style="margin: 5px 0 0 0; color: #718096; font-size: 14px;">
                    Нажмите на кнопку ниже и отправьте команду <code>/start</code>
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    bot_link = notification_service.bot.get_bot_link(st.session_state.client_phone)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(
            f"""
            <a href="{bot_link}" target="_blank" style="text-decoration: none;">
                <button style="background: linear-gradient(135deg, #0088cc 0%, #006699 100%); 
                     color: white; padding: 16px 24px; border: none; border-radius: 12px; 
                     width: 100%; font-size: 16px; font-weight: 600; cursor: pointer;
                     box-shadow: 0 4px 12px rgba(0, 136, 204, 0.3);
                     display: flex; align-items: center; justify-content: center; gap: 10px;">
                    <span style="font-size: 24px;">✈️</span>
                    <span>Открыть бота в Telegram</span>
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        if not is_completed:
            if st.button("✅ Готово", use_container_width=True, key="step1_done"):
                st.session_state.telegram_step_completed[1] = True
                st.rerun()
        else:
            st.success("✅ Выполнено")
    
    if not is_completed:
        with st.expander("❓ Что делать в боте?"):
            st.markdown("""
            После открытия бота:
            1. Нажмите кнопку **"Start"** или отправьте команду `/start`
            2. Бот пришлёт вам приветственное сообщение
            3. Готово! Переходите к следующему шагу
            
            **Важно:** Без нажатия Start бот не сможет отправлять вам сообщения
            """)

def render_step_2():
    """Шаг 2: Получить Chat ID"""
    step1_completed = st.session_state.telegram_step_completed.get(1, False)
    is_completed = st.session_state.telegram_step_completed.get(2, False)
    
    # Блокируем шаг, если не выполнен предыдущий
    is_locked = not step1_completed
    
    border_color = "#88c8bc" if is_completed else ("#e2e8f0" if is_locked else "#cbd5e0")
    bg_color = "rgba(136, 200, 188, 0.05)" if is_completed else ("rgba(226, 232, 240, 0.3)" if is_locked else "white")
    
    st.markdown(f"""
    <div style="background: {bg_color}; padding: 25px; border-radius: 16px; 
         border: 2px solid {border_color}; margin-bottom: 20px;
         box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); 
         {('opacity: 0.6;' if is_locked else '')}">
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
            <div style="background: {'linear-gradient(135deg, #88c8bc 0%, #6ba292 100%)' if is_completed else ('#e2e8f0' if is_locked else 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)')}; 
                 color: {'white' if is_completed or not is_locked else '#718096'}; 
                 width: 48px; height: 48px; border-radius: 50%; 
                 display: flex; align-items: center; justify-content: center; 
                 font-size: 24px; font-weight: bold; flex-shrink: 0;">
                {'✓' if is_completed else ('🔒' if is_locked else '2')}
            </div>
            <div>
                <h4 style="margin: 0; color: #2d3748; font-size: 20px;">Узнайте ваш Chat ID</h4>
                <p style="margin: 5px 0 0 0; color: #718096; font-size: 14px;">
                    Chat ID — это просто число, которое идентифицирует ваш аккаунт
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if is_locked:
        st.info("🔒 Сначала завершите Шаг 1")
        return
    
    userinfo_link = "https://t.me/userinfobot"
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(
            f"""
            <a href="{userinfo_link}" target="_blank" style="text-decoration: none;">
                <button style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                     color: white; padding: 16px 24px; border: none; border-radius: 12px; 
                     width: 100%; font-size: 16px; font-weight: 600; cursor: pointer;
                     box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
                     display: flex; align-items: center; justify-content: center; gap: 10px;">
                    <span style="font-size: 24px;">🤖</span>
                    <span>Открыть @userinfobot</span>
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        if not is_completed:
            if st.button("✅ Готово", use_container_width=True, key="step2_done"):
                st.session_state.telegram_step_completed[2] = True
                st.rerun()
        else:
            st.success("✅ Выполнено")
    
    if not is_completed:
        with st.expander("❓ Как получить Chat ID?"):
            st.markdown("""
            После открытия @userinfobot:
            1. Нажмите **"Start"** или отправьте `/start`
            2. Бот сразу пришлёт вам ответ с вашим **ID** (это просто число)
            3. **Скопируйте это число** — оно понадобится на следующем шаге
            
            **Пример:** Бот может прислать "Your ID: `123456789`" — вам нужно скопировать `123456789`
            
            **Подсказка:** Обычно Chat ID состоит из 9-10 цифр
            """)

def render_step_3(notification_service):
    """Шаг 3: Ввести Chat ID"""
    step2_completed = st.session_state.telegram_step_completed.get(2, False)
    
    is_locked = not step2_completed
    
    border_color = "#cbd5e0" if is_locked else "#88c8bc"
    bg_color = "rgba(226, 232, 240, 0.3)" if is_locked else "white"
    
    st.markdown(f"""
    <div style="background: {bg_color}; padding: 25px; border-radius: 16px; 
         border: 2px solid {border_color}; margin-bottom: 20px;
         box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
         {('opacity: 0.6;' if is_locked else '')}">
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
            <div style="background: {'#e2e8f0' if is_locked else 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'}; 
                 color: {'#718096' if is_locked else 'white'}; 
                 width: 48px; height: 48px; border-radius: 50%; 
                 display: flex; align-items: center; justify-content: center; 
                 font-size: 24px; font-weight: bold; flex-shrink: 0;">
                {'🔒' if is_locked else '3'}
            </div>
            <div>
                <h4 style="margin: 0; color: #2d3748; font-size: 20px;">Введите ваш Chat ID</h4>
                <p style="margin: 5px 0 0 0; color: #718096; font-size: 14px;">
                    Вставьте число, которое прислал вам @userinfobot
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if is_locked:
        st.info("🔒 Сначала завершите Шаг 2")
        return
    
    with st.form("connect_telegram_form", clear_on_submit=False):
        st.markdown("#### 📝 Введите данные")
        
        chat_id = st.text_input(
            "Chat ID (только цифры)",
            placeholder="Например: 123456789",
            help="Вставьте число, которое вы получили от @userinfobot",
            key="chat_id_input"
        )
        
        # Подсказка с примером
        st.markdown("""
        <div style="background: rgba(136, 200, 188, 0.1); padding: 15px; border-radius: 8px; 
             border-left: 3px solid #88c8bc; margin: 15px 0;">
            <strong>💡 Подсказка:</strong> Chat ID — это просто число из 9-10 цифр.<br>
            Пример правильного формата: <code>123456789</code>
        </div>
        """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button(
            "🎯 Подключить уведомления",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            if not chat_id:
                st.error("❌ Введите Chat ID")
            elif not chat_id.isdigit():
                st.error("❌ Chat ID должен содержать только цифры (без пробелов и других символов)")
            elif len(chat_id) < 8:
                st.error("❌ Chat ID слишком короткий. Проверьте, правильно ли вы скопировали число")
            else:
                with st.spinner("🔄 Проверяем подключение..."):
                    # Проверяем, может ли бот отправить сообщение
                    test_message = """
✅ <b>Подключение успешно!</b>

Теперь вы будете получать:
• ✅ Подтверждения записей
• ⏰ Напоминания за 1 час до консультаций
• 💳 Уведомления об оплате
• ❌ Информацию об отменах

<i>Добро пожаловать в систему уведомлений!</i>
                    """
                    
                    if notification_service.bot.send_to_client(chat_id, test_message):
                        # Сохраняем chat_id
                        if notification_service.save_telegram_chat_id(st.session_state.client_phone, chat_id):
                            st.balloons()
                            st.success("🎉 Отлично! Telegram успешно подключен!")
                            st.info("📱 Проверьте Telegram — мы отправили вам подтверждение")
                            
                            # Сбрасываем состояние
                            st.session_state.telegram_step_completed = {1: False, 2: False}
                            
                            # Задержка перед перезагрузкой
                            import time
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("❌ Не удалось сохранить настройки. Попробуйте ещё раз")
                    else:
                        st.error("""
                        ❌ Не удалось отправить сообщение
                        
                        **Возможные причины:**
                        1. Вы не нажали Start в нашем боте (Шаг 1)
                        2. Неправильный Chat ID
                        3. Вы заблокировали бота
                        
                        **Что делать:**
                        • Убедитесь, что вы выполнили Шаг 1
                        • Проверьте правильность введённого Chat ID
                        • Попробуйте ещё раз
                        """)
    
    # Дополнительная помощь
    with st.expander("❓ Нужна помощь?"):
        st.markdown("""
        ### Частые вопросы:
        
        **Q: Где найти Chat ID?**
        A: Откройте @userinfobot в Telegram, нажмите Start — бот сразу пришлёт ваш ID
        
        **Q: Что делать, если Chat ID не принимается?**
        A: 
        - Убедитесь, что скопировали только цифры (без букв и символов)
        - Проверьте, что нажали Start в нашем боте (Шаг 1)
        - Попробуйте обновить страницу и начать заново
        
        **Q: Безопасно ли делиться Chat ID?**
        A: Да, Chat ID не даёт доступа к вашему аккаунту. Это просто идентификатор для отправки сообщений.
        
        **Q: Могу ли я отключить уведомления?**
        A: Да, после подключения появится кнопка отключения уведомлений.
        """)