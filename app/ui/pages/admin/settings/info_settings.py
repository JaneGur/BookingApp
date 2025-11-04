import streamlit as st
from services.settings_service import SettingsService
from ui.components import render_info_panel

def render_info_settings(settings_service):
    """Настройки информационной панели"""
    st.markdown("#### ℹ️ Настройки информационной панели")
    st.info("Здесь вы можете редактировать текст, который видят клиенты в правой панели")
    
    settings = settings_service.get_settings()
    if settings:
        with st.form("info_panel_settings"):
            st.markdown("**Основные настройки:**")
            info_title = st.text_input("📝 Заголовок панели", 
                                     value=settings.info_title)
            
            st.markdown("**📋 Содержимое панели:**")
            info_work_hours = st.text_area("🕐 Рабочее время", 
                                         value=settings.info_work_hours,
                                         height=80,
                                         help="Используйте \\n для переноса строк")
            
            info_session_duration = st.text_area("⏱️ Длительность консультации", 
                                               value=settings.info_session_duration,
                                               height=80)
            
            info_format = st.text_area("💻 Формат консультации", 
                                     value=settings.info_format,
                                     height=80)
            
            info_contacts = st.text_area("📞 Контактная информация", 
                                       value=settings.info_contacts,
                                       height=100,
                                       help="Укажите телефоны, email, сайт и другие контакты")
            
            info_additional = st.text_area("📝 Дополнительная информация", 
                                         value=settings.info_additional,
                                         height=100,
                                         placeholder="Любая дополнительная информация для клиентов...",
                                         help="Необязательное поле")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submit_info = st.form_submit_button("💾 Сохранить настройки", width='stretch')
            with col2:
                preview_info = st.form_submit_button("👁️ Предпросмотр", width='stretch')
            
            if submit_info:
                info_data = {
                    'info_title': info_title,
                    'info_work_hours': info_work_hours,
                    'info_session_duration': info_session_duration,
                    'info_format': info_format,
                    'info_contacts': info_contacts,
                    'info_additional': info_additional
                }
                
                if settings_service.update_settings(info_data):
                    st.success("✅ Настройки информационной панели сохранены!")
                    st.rerun()
                else:
                    st.error("❌ Ошибка сохранения настроек.")
            
            if preview_info:
                st.markdown("---")
                st.markdown("#### 👁️ Предпросмотр информационной панели")
                render_info_panel()