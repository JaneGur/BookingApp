import streamlit as st

def load_animation_styles():
    """Стили для анимаций и переходов"""
    st.markdown("""
    <style>
    /* ===== АНИМАЦИИ ===== */
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
    
    .booking-card, .action-card {
        animation: fadeIn 0.3s ease;
    }
    
    /* ===== ПЛАВНЫЕ ПЕРЕХОДЫ ===== */
    .stButton>button,
    .action-card,
    .booking-card,
    .stTabs [data-baseweb="tab"],
    div[role="radiogroup"] > label {
        transition: all 0.2s ease;
    }
    </style>
    """, unsafe_allow_html=True)