import streamlit as st
from services.settings_service import SettingsService

def render_info_panel():
    """Современная сбалансированная информационная панель"""
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

    # Обертка для sticky эффекта (прилипает при прокрутке)
    st.markdown('<div class="info-panel-wrapper">', unsafe_allow_html=True)

    # Улучшенные стили
    st.markdown("""
    <style>
    .info-panel-wrapper {
        position: sticky;
        top: 1rem;
        max-height: calc(100vh - 2rem);
        overflow-y: auto;
        overflow-x: hidden;
    }
    
    .info-panel-wrapper::-webkit-scrollbar {
        width: 4px;
    }
    
    .info-panel-wrapper::-webkit-scrollbar-track {
        background: transparent;
    }
    
    .info-panel-wrapper::-webkit-scrollbar-thumb {
        background-color: rgba(136, 200, 188, 0.3);
        border-radius: 10px;
    }
    
    .info-section {
        background: linear-gradient(135deg, rgba(136, 200, 188, 0.08) 0%, rgba(168, 213, 186, 0.08) 100%);
        border-radius: 16px;
        padding: 1.75rem;
        margin-bottom: 1.25rem;
        border: 1px solid rgba(136, 200, 188, 0.2);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
        transition: all 0.2s ease;
    }
    
    .info-section:hover {
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.05);
    }
    
    .info-section h4 {
        color: #225c52;
        margin: 0 0 1.25rem 0;
        font-size: 1.15rem;
        font-weight: 600;
    }
    
    .info-item {
        display: flex;
        align-items: flex-start;
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    
    .info-item:last-child {
        margin-bottom: 0;
    }
    
    .info-icon {
        font-size: 1.3rem;
        margin-right: 0.85rem;
        min-width: 26px;
        flex-shrink: 0;
    }
    
    .info-content {
        color: #4a6a60;
        font-size: 0.98rem;
        line-height: 1.5;
    }
    
    .info-label {
        font-weight: 600;
        color: #225c52;
        display: block;
        margin-bottom: 0.25rem;
    }
    
    .highlight-box {
        background: rgba(136, 200, 188, 0.15);
        border-left: 3px solid #88c8bc;
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin: 1.25rem 0;
    }
    
    @media (max-width: 768px) {
        .info-panel-wrapper {
            position: static;
            max-height: none;
            overflow-y: visible;
        }
        
        .info-section {
            padding: 1.25rem !important;
            margin-bottom: 1rem !important;
        }
        
        .info-section h4 {
            font-size: 1.05rem !important;
        }
        
        .info-content {
            font-size: 0.92rem !important;
        }
        
        .info-icon {
            font-size: 1.15rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Основная информация
    st.markdown('<div class="info-section">', unsafe_allow_html=True)
    st.markdown('<h4>ℹ️ Информация о консультациях</h4>', unsafe_allow_html=True)
    
    # Рабочее время
    work_hours = settings.info_work_hours.replace('\n', ' ')
    st.markdown(f"""
    <div class="info-item">
        <div class="info-icon">🕐</div>
        <div class="info-content">
            <span class="info-label">Рабочее время</span>
            {work_hours}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Длительность
    duration = settings.info_session_duration.replace('\n', ' ')
    st.markdown(f"""
    <div class="info-item">
        <div class="info-icon">⏱️</div>
        <div class="info-content">
            <span class="info-label">Длительность</span>
            {duration}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Формат
    format_info = settings.info_format.replace('\n', ' ')
    st.markdown(f"""
    <div class="info-item">
        <div class="info-icon">💻</div>
        <div class="info-content">
            <span class="info-label">Формат</span>
            {format_info}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Продукт по умолчанию (если есть)
    if default_product_name and default_product_price:
        st.markdown(f"""
        <div class="highlight-box">
            <div class="info-item" style="margin: 0;">
                <div class="info-icon">💳</div>
                <div class="info-content">
                    <span class="info-label">{default_product_name}</span>
                    <span style="font-size: 1.2rem; font-weight: 600; color: #225c52; display: block; margin-top: 0.35rem;">{default_product_price:,.0f} ₽</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Контакты
    st.markdown('<div class="info-section">', unsafe_allow_html=True)
    st.markdown('<h4>📞 Контакты</h4>', unsafe_allow_html=True)
    
    contacts = settings.info_contacts
    contact_lines = [line.strip() for line in contacts.split('\n') if line.strip()]
    
    for line in contact_lines:
        if 'Контакты:' in line:
            continue
        
        # Определяем иконку
        icon = "📱"
        if "📱" in line or "+" in line:
            icon = "📱"
        elif "📧" in line or "@" in line:
            icon = "📧"
        elif "🌿" in line or "http" in line or "www" in line:
            icon = "🌐"
        elif "💬" in line or "telegram" in line.lower():
            icon = "💬"
        
        clean_line = line.replace("📱", "").replace("📧", "").replace("🌿", "").replace("💬", "").strip()
        
        if clean_line:
            st.markdown(f"""
            <div class="info-item">
                <div class="info-icon">{icon}</div>
                <div class="info-content">{clean_line}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Дополнительная информация (если есть)
    if settings.info_additional and settings.info_additional.strip():
        st.markdown('<div class="info-section">', unsafe_allow_html=True)
        st.markdown('<h4>📝 Дополнительно</h4>', unsafe_allow_html=True)
        additional_paras = settings.info_additional.strip().split('\n\n')
        for para in additional_paras:
            if para.strip():
                st.markdown(f'<div class="info-content" style="margin-bottom: 0.75rem;">{para.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Закрываем обертку
    st.markdown('</div>', unsafe_allow_html=True)