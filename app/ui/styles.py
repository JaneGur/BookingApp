import streamlit as st

def load_custom_css():
    """Элегантные премиум стили с современным дизайном"""
    st.markdown("""
        <style>
        /* ===== ШРИФТЫ ===== */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class^="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            letter-spacing: -0.01em;
            -webkit-font-smoothing: antialiased;
        }

        /* ===== МЯГКИЙ ГРАДИЕНТНЫЙ ФОН ===== */
        .main {
            padding: 0rem 1rem;
            background: 
                radial-gradient(circle at 20% 20%, rgba(136, 200, 188, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(168, 213, 186, 0.08) 0%, transparent 50%),
                linear-gradient(135deg, #f8fbfa 0%, #f2f7f5 100%);
        }
        
        /* ===== КНОПКИ С СОВРЕМЕННЫМ ЭФФЕКТОМ ===== */
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            height: 3.2em;
            background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%);
            color: white;
            font-weight: 600;
            border: none;
            box-shadow: 0 2px 8px rgba(136, 200, 188, 0.25);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-size: 0.95rem;
        }
        
        .stButton>button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(136, 200, 188, 0.35);
        }

        .stButton>button:active {
            transform: scale(0.98);
        }
        
        /* ===== ЧИСТЫЕ КАРТОЧКИ ===== */
        .booking-card {
            padding: 2rem;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.95);
            margin-bottom: 1.5rem;
            border: 1px solid rgba(136, 200, 188, 0.15);
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
            transition: all 0.25s ease;
        }
        
        .booking-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border-color: rgba(136, 200, 188, 0.25);
        }
        
        /* ===== ИНФОРМАЦИОННЫЕ БЛОКИ ===== */
        .info-box {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
            border: 1px solid rgba(136, 200, 188, 0.15);
            transition: all 0.2s ease;
        }
        
        .info-box:hover {
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
        }
        
        /* ===== ПРИВЕТСТВЕННЫЙ ХЕДЕР ===== */
        .welcome-header {
            background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%);
            color: white;
            padding: 3rem 2.5rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 8px 24px rgba(136, 200, 188, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .welcome-header h1 { 
            font-weight: 700;
            letter-spacing: -0.02em;
            margin-bottom: 0.5rem;
        }
        .welcome-header p { 
            opacity: 0.95;
            font-weight: 400;
        }
        
        /* ===== TELEGRAM СТАТУСЫ ===== */
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
        
        /* ===== САЙДБАР ===== */
        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.98);
            border-right: 1px solid rgba(0, 0, 0, 0.06);
        }

        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4 { 
            letter-spacing: -0.01em;
            font-weight: 600;
        }

        /* ===== НАВИГАЦИОННЫЕ ВКЛАДКИ ===== */
        .stTabs [role="tablist"] button {
            border: none;
            background: transparent;
            color: #5a7a6f;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        
        .stTabs [role="tablist"] button:hover {
            color: #3d6f63;
        }
        
        .stTabs [role="tablist"] button[aria-selected="true"] {
            color: #225c52;
            position: relative;
        }
        
        .stTabs [role="tablist"] button[aria-selected="true"]::after {
            content: "";
            position: absolute;
            left: 10%;
            right: 10%;
            bottom: -8px;
            height: 3px;
            border-radius: 3px;
            background: linear-gradient(90deg, #88c8bc, #6ba292);
        }

        /* ===== INPUTS С ЧИСТЫМ ДИЗАЙНОМ ===== */
        .stTextInput input, .stTextArea textarea, 
        .stSelectbox select, .stDateInput input, 
        .stTimeInput input {
            border-radius: 10px !important;
            border: 1.5px solid rgba(136, 200, 188, 0.25) !important;
            background: rgba(255, 255, 255, 0.95) !important;
            transition: all 0.2s ease;
        }
        
        .stTextInput input:focus, .stTextArea textarea:focus, 
        .stSelectbox select:focus, .stDateInput input:focus, 
        .stTimeInput input:focus {
            outline: none !important;
            border-color: #88c8bc !important;
            box-shadow: 0 0 0 3px rgba(136, 200, 188, 0.1);
        }

        /* ===== МЕТРИКИ ===== */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 1.2rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            border: 1px solid rgba(136, 200, 188, 0.15);
            transition: all 0.2s ease;
        }
        
        [data-testid="stMetric"]:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }
        
        [data-testid="stMetricValue"] { 
            color: #225c52;
            font-weight: 700;
        }
        
        /* ===== SCROLLBAR ===== */
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
        
        /* ===== АЛЕРТЫ ===== */
        .stAlert {
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        /* ===== РАДИО НАВИГАЦИЯ (CHIP STYLE) ===== */
        div[role="radiogroup"] {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        div[role="radiogroup"] > label {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            border-radius: 20px;
            border: 1.5px solid rgba(136, 200, 188, 0.25);
            background: rgba(255, 255, 255, 0.9);
            color: #4a6a60;
            font-weight: 500;
            transition: all 0.2s ease;
            cursor: pointer;
        }
        
        div[role="radiogroup"] > label:hover {
            border-color: rgba(136, 200, 188, 0.5);
            transform: translateY(-1px);
        }
        
        div[role="radiogroup"] input[type="radio"] {
            display: none;
        }
        
        div[role="radiogroup"] input[type="radio"]:checked + div {
            color: #225c52;
            background: rgba(136, 200, 188, 0.15);
            border-color: #88c8bc;
            font-weight: 600;
        }
        
        </style>
    """, unsafe_allow_html=True)