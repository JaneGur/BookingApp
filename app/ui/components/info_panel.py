import streamlit as st
from services.settings_service import SettingsService

def render_info_panel():
    """Отображение информационной панели с настраиваемым содержимым"""
    settings_service = SettingsService()
    settings = settings_service.get_settings()
    
    if not settings:
        return
    
    # Определяем продукт по умолчанию (featured)
    default_product_name = None
    default_product_price = None
    try:
        from core.database import db_manager
        sb = db_manager.get_client()
        if sb is not None:
            rows = sb.table('products').select('name,price_rub,is_featured,is_active').eq('is_active', True).order('sort_order').execute().data or []
            featured = [p for p in rows if p.get('is_featured')]
            chosen = (featured[0] if featured else (rows[0] if rows else None))
            if chosen:
                default_product_name = chosen.get('name')
                default_product_price = chosen.get('price_rub')
    except Exception:
        pass

    # Формируем HTML содержимое
    info_html = f"""
    <div class="info-box">
        <h4>{settings.info_title}</h4>
        <p><strong>{settings.info_work_hours.replace(chr(10), '<br>')}</strong></p>
        <p><strong>{settings.info_session_duration.replace(chr(10), '<br>')}</strong></p>
        <p><strong>{settings.info_format.replace(chr(10), '<br>')}</strong></p>
        {('<p><strong>💳 Продукт по умолчанию:</strong> ' + default_product_name + ((' — ' + str(default_product_price) + ' ₽') if default_product_price is not None else '') + '</p>') if default_product_name else ''}
        <hr>
        <h4>📞 Контакты</h4>
        <p>{settings.info_contacts.replace(chr(10), '<br>')}</p>
    """
    
    if settings.info_additional and settings.info_additional.strip():
        info_html += f'<p>{settings.info_additional.replace(chr(10), "<br>")}</p>'
    
    info_html += "</div>"
    
    st.markdown(info_html, unsafe_allow_html=True)