import streamlit as st
from services.notification_service import NotificationService
from config.settings import config

def render_notifications_settings(notification_service):
    """Настройка уведомлений"""
    st.markdown("#### 🔔 Настройка уведомлений")
    
    # Статус бота
    if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_ADMIN_CHAT_ID:
        st.success("✅ Бот настроен и готов к работе")
        
        # Информация о боте
        try:
            bot_info = notification_service.bot.get_bot_info()
            if bot_info:
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.write(f"**🤖 Имя бота:** {bot_info.get('first_name', 'Неизвестно')}")
                    st.write(f"**👤 Username:** @{bot_info.get('username', 'Неизвестно')}")
                with col_info2:
                    st.write(f"**💬 Chat ID админа:** {config.TELEGRAM_ADMIN_CHAT_ID}")
                    st.write(f"**🆔 ID бота:** {bot_info.get('id', 'Неизвестно')}")
        except Exception:
            st.info("ℹ️ Информация о боте недоступна")
        
        # Тестирование уведомлений
        st.markdown("---")
        st.markdown("##### 🧪 Тестирование уведомлений")
        
        test_message = st.text_area("Тестовое сообщение", 
                                  "✅ Система уведомлений работает корректно!",
                                  height=100)
        
        col_test1, col_test2 = st.columns(2)
        with col_test1:
            if st.button("📤 Тест админу", use_container_width=True):
                if notification_service.bot.send_to_admin(test_message):
                    st.success("✅ Тест отправлен админу!")
                else:
                    st.error("❌ Ошибка отправки")
        
        with col_test2:
            test_chat_id = st.text_input("Chat ID для теста", placeholder="123456789")
            if st.button("📤 Тест клиенту", use_container_width=True, disabled=not test_chat_id):
                try:
                    if notification_service.bot.send_message(test_chat_id, test_message):
                        st.success("✅ Тест отправлен клиенту!")
                    else:
                        st.error("❌ Ошибка отправки клиенту")
                except Exception as e:
                    st.error(f"❌ Ошибка: {e}")
        
        # Статистика (заглушка для будущей реализации)
        st.markdown("---")
        st.markdown("##### 📊 Статистика уведомлений")
        st.info("📈 Статистика отправки уведомлений появится в будущих обновлениях")
        
    else:
        st.error("❌ Telegram бот не настроен")
        st.markdown("""
        ### 📝 Инструкция по настройке:
        
        1. **Создайте бота** через [@BotFather](https://t.me/BotFather) в Telegram
        2. **Получите токен** и укажите его в переменной окружения `TELEGRAM_BOT_TOKEN`
        3. **Узнайте ваш Chat ID** и укажите его в `TELEGRAM_ADMIN_CHAT_ID`
        4. **Перезапустите приложение**
        
        После настройки бот будет автоматически отправлять уведомления о новых записях и напоминания.
        """)