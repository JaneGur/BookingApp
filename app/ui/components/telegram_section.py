import streamlit as st
from services.notification_service import NotificationService
from services.booking_service import BookingService
from utils.validators import normalize_phone, hash_password

def render_telegram_section():
    """Отображение секции подключения Telegram"""
    st.markdown("### 💬 Уведомления в Telegram")
    
    notification_service = NotificationService()
    booking_service = BookingService()
    
    # Получаем текущий chat_id клиента
    current_chat_id = notification_service.get_client_telegram_chat_id(st.session_state.client_phone)
    
    if current_chat_id:
        # Telegram уже подключен
        st.markdown("""
        <div class="telegram-connected">
            <h4>✅ Telegram подключен!</h4>
            <p>Вы получаете уведомления о всех событиях</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.info("""
            **Вы получаете:**
            • ✅ Подтверждения новых записей
            • ⏰ Напоминания за 1 час до консультаций  
            • ❌ Уведомления об отменах
            """)
        
        with col2:
            if st.button("🔄 Отправить тест", use_container_width=True):
                if notification_service.bot.send_to_client(current_chat_id, "✅ Тестовое уведомление работает!"):
                    st.success("✅ Тестовое уведомление отправлено!")
                else:
                    st.error("❌ Ошибка отправки")
        
        with col3:
            if st.button("📋 Мои записи", use_container_width=True):
                upcoming_bookings = booking_service.get_upcoming_client_booking(st.session_state.client_phone)
                if upcoming_bookings:
                    st.success("✅ Информация о записях выше")
                else:
                    st.error("❌ Нет предстоящих записей")
        
    else:
        # Telegram не подключен
        st.markdown("""
        <div class="telegram-disconnected">
            <h4>⚠️ Telegram не подключен</h4>
            <p>Вы не получаете уведомления о записях и напоминания</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Подключение без сложностей: 3 шага")

        # Ссылки
        bot_link = notification_service.bot.get_bot_link(st.session_state.client_phone)
        userinfo_link = "https://t.me/userinfobot"

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.markdown(
                f"<a href=\"{bot_link}\" target=\"_blank\"><button style=\"background:#0088cc;color:#fff;padding:12px;border:none;border-radius:10px;width:100%\">1) Откройте нашего бота и нажмите Start</button></a>",
                unsafe_allow_html=True
            )
        with col_btn2:
            st.markdown(
                f"<a href=\"{userinfo_link}\" target=\"_blank\"><button style=\"background:#666;color:#fff;padding:12px;border:none;border-radius:10px;width:100%\">2) Узнать свой Chat ID (нажмите Start)</button></a>",
                unsafe_allow_html=True
            )

        st.markdown(
            """
            • Шаг 1 обязателен: в нашем боте нажмите «Start», иначе сообщения не будут доставляться.
            • Шаг 2: в @userinfobot нажмите «Start» — бот пришлёт ваш Chat ID (это просто число, без + и без @).
            • Шаг 3: вставьте это число ниже и нажмите «Сохранить и подключить».
            После этого вы начнёте получать:
            • ✅ Подтверждения новых записей
            • ⏰ Напоминания за 1 час до консультации
            • ❌ Уведомления об отменах
            """
        )

        with st.form("connect_telegram_form"):
            chat_id = st.text_input(
                "Введите ваш Chat ID (только цифры)",
                placeholder="Например, 123456789",
                help="В @userinfobot — нажмите Start, скопируйте число из ответа"
            )

            submitted = st.form_submit_button("💾 Сохранить и подключить", use_container_width=True)

            if submitted:
                if not chat_id:
                    st.error("❌ Введите Chat ID")
                elif not chat_id.isdigit():
                    st.error("❌ Chat ID должен содержать только цифры")
                else:
                    # Проверяем подключение
                    if notification_service.bot.check_client_connection(chat_id):
                        # Сохраняем и подключаем
                        success = notification_service.save_telegram_chat_id(
                            st.session_state.client_phone,
                            chat_id
                        )

                        if success:
                            st.success("🎉 Telegram успешно подключен! Вы будете получать уведомления.")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Ошибка при сохранении настроек")
                    else:
                        st.error("❌ Не удалось отправить сообщение. Проверьте Chat ID и попробуйте ещё раз.")