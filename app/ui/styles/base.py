from .components.buttons import get_button_styles
from .components.cards import get_card_styles
from .components.navigation import get_navigation_styles
from .components.forms import get_form_styles
from .components.layout import get_layout_styles
from .pages.public import get_public_page_styles
from .utils.responsive import get_responsive_styles

def load_custom_css():
    """Элегантные премиум стили с улучшенной навигацией"""
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
    .main {
        padding: 0rem 1rem;
        background: 
            radial-gradient(circle at 20% 20%, rgba(136, 200, 188, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(168, 213, 186, 0.08) 0%, transparent 50%),
            linear-gradient(135deg, #f8fbfa 0%, #f2f7f5 100%);
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
    /* Telegram статусы */
    .telegram-connected {
        background: linear-gradient(135deg, rgba(227, 242, 253, 0.95) 0%, rgba(187, 222, 251, 0.95) 100%);
        border-left: 3px solid #0088cc;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 136, 204, 0.12);
    }
    
    .telegram-disconnected {
        background: linear-gradient(135deg, rgba(255, 243, 224, 0.95) 0%, rgba(255, 224, 178, 0.95) 100%);
        border-left: 3px solid #ff9800;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(255, 152, 0, 0.12);
    }
    """