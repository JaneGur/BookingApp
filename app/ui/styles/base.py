from .components.buttons import get_button_styles
from .components.cards import get_card_styles
from .components.navigation import get_navigation_styles
from .components.forms import get_form_styles
from .components.layout import get_layout_styles
from .pages.public import get_public_page_styles
from .utils.responsive import get_responsive_styles

def load_custom_css():
    """Элегантные премиум стили с улучшенной навигацией и фоном"""
    import streamlit as st
    
    css_components = [
        _get_fonts_and_base(),
        _get_main_styles(),
        get_navigation_styles(),
        get_button_styles(),
        get_card_styles(),
        get_form_styles(),
        get_layout_styles(),
        get_public_page_styles(),
        get_responsive_styles(),
        _get_scrollbar_styles(),
        _get_animations(),
        _get_status_styles(),
        _get_telegram_styles()
    ]
    
    full_css = "\n".join(css_components)
    st.markdown(f"<style>{full_css}</style>", unsafe_allow_html=True)

def _get_fonts_and_base():
    return """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class^="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        letter-spacing: -0.01em;
        -webkit-font-smoothing: antialiased;
    }
    """

def _get_main_styles():
    return """
    /* Основной фон с многослойными эффектами */
    .main {
        padding: 0rem 1rem;
        background: 
            /* Тонкая сетка */
            repeating-linear-gradient(
                0deg,
                rgba(136, 200, 188, 0.015) 0px,
                transparent 1px,
                transparent 40px,
                rgba(136, 200, 188, 0.015) 41px
            ),
            repeating-linear-gradient(
                90deg,
                rgba(136, 200, 188, 0.015) 0px,
                transparent 1px,
                transparent 40px,
                rgba(136, 200, 188, 0.015) 41px
            ),
            /* Органические пятна света */
            radial-gradient(ellipse at 10% 15%, rgba(136, 200, 188, 0.06) 0%, transparent 40%),
            radial-gradient(ellipse at 90% 85%, rgba(168, 213, 186, 0.05) 0%, transparent 40%),
            radial-gradient(ellipse at 50% 50%, rgba(232, 245, 242, 0.3) 0%, transparent 60%),
            /* Мягкий волновой градиент */
            linear-gradient(
                135deg,
                #fafdfb 0%,
                #f5faf8 25%,
                #f8fbfa 50%,
                #f2f7f5 75%,
                #f0f6f4 100%
            );
        background-attachment: fixed;
        position: relative;
    }
    
    /* Декоративные элементы поверх фона */
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        pointer-events: none;
        background: 
            /* Тонкие волны */
            radial-gradient(
                ellipse 800px 400px at 20% 20%,
                rgba(136, 200, 188, 0.03) 0%,
                transparent 50%
            ),
            radial-gradient(
                ellipse 600px 300px at 80% 80%,
                rgba(168, 213, 186, 0.025) 0%,
                transparent 50%
            );
        opacity: 0.8;
        z-index: 0;
    }
    
    /* Все контент поверх фона */
    .main > div {
        position: relative;
        z-index: 1;
    }
    
    /* Улучшенные карточки с мягкой тенью на новом фоне */
    .booking-card, .action-card, .info-section {
        background: rgba(255, 255, 255, 0.92) !important;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(136, 200, 188, 0.12);
    }
    
    /* Header с полупрозрачностью */
    [data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
    }
    """

def _get_scrollbar_styles():
    return """
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(240, 242, 245, 0.5);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #88c8bc, #6ba292);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #6ba292;
    }
    """

def _get_animations():
    return """
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    """

def _get_status_styles():
    return """
    /* Метки статуса */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    .status-badge.success {
        background: rgba(136, 200, 188, 0.2);
        color: #2d5a4f;
    }
    
    .status-badge.warning {
        background: rgba(255, 193, 7, 0.2);
        color: #856404;
    }
    
    .status-badge.danger {
        background: rgba(220, 53, 69, 0.2);
        color: #721c24;
    }
    """

def _get_telegram_styles():
    return """
    /* Telegram статусы с улучшенным дизайном */
    .telegram-connected {
        background: 
            linear-gradient(135deg, rgba(227, 242, 253, 0.95) 0%, rgba(187, 222, 251, 0.95) 100%);
        border-left: 4px solid #0088cc;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 
            0 4px 12px rgba(0, 136, 204, 0.08),
            0 2px 4px rgba(0, 136, 204, 0.06);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(0, 136, 204, 0.1);
        position: relative;
    }
    
    .telegram-disconnected {
        background: 
            linear-gradient(135deg, rgba(255, 243, 224, 0.95) 0%, rgba(255, 224, 178, 0.95) 100%);
        border-left: 4px solid #ff9800;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 
            0 4px 12px rgba(255, 152, 0, 0.08),
            0 2px 4px rgba(255, 152, 0, 0.06);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 152, 0, 0.1);
        position: relative;
    }
    
    /* Декоративные элементы для блоков */
    .telegram-connected::before,
    .telegram-disconnected::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 150px;
        height: 150px;
        opacity: 0.05;
        border-radius: 50%;
        pointer-events: none;
    }
    
    .telegram-connected::before {
        background: radial-gradient(circle, #0088cc 0%, transparent 70%);
    }
    
    .telegram-disconnected::before {
        background: radial-gradient(circle, #ff9800 0%, transparent 70%);
    }
    """