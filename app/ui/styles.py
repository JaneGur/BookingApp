import streamlit as st

def load_custom_css():
    """Элегантные премиум стили с улучшенной навигацией"""
    st.markdown("""
        <style>
        /* ===== СУЩЕСТВУЮЩИЕ СТИЛИ ===== */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class^="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            letter-spacing: -0.01em;
            -webkit-font-smoothing: antialiased;
        }

        .main {
            padding: 0rem 1rem;
            background: 
                radial-gradient(circle at 20% 20%, rgba(136, 200, 188, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(168, 213, 186, 0.08) 0%, transparent 50%),
                linear-gradient(135deg, #f8fbfa 0%, #f2f7f5 100%);
        }
        
        
        /* ===== НОВЫЕ СТИЛИ ДЛЯ УЛУЧШЕННОЙ НАВИГАЦИИ ===== */
        
        /* Контейнер навигации */
        .stTabs {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 0.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
            border: 1px solid rgba(136, 200, 188, 0.15);
        }
        
        /* Вкладки навигации */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: transparent;
            border-bottom: none;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: auto;
            padding: 0.75rem 1.5rem;
            border-radius: 10px;
            background: transparent;
            border: 1px solid transparent;
            color: #5a7a6f;
            font-weight: 500;
            font-size: 0.95rem;
            transition: all 0.2s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(136, 200, 188, 0.08);
            border-color: rgba(136, 200, 188, 0.2);
            color: #3d6f63;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%) !important;
            color: white !important;
            border-color: transparent !important;
            box-shadow: 0 2px 8px rgba(136, 200, 188, 0.3);
        }
        
        /* Индикатор активной вкладки */
        .stTabs [data-baseweb="tab-border"] {
            display: none;
        }
        
        /* Контент вкладок */
        .stTabs [data-baseweb="tab-panel"] {
            padding: 1.5rem 0;
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
        
        /* Вторичные кнопки (для хедера аутентификации) */
        .stButton>button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.95);
            color: #225c52;
            border: 2px solid rgba(136, 200, 188, 0.3);
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        }
        
        .stButton>button[kind="secondary"]:hover {
            background: rgba(136, 200, 188, 0.1);
            border-color: #88c8bc;
            color: #225c52;
        }
        
        
        /* ===== КАРТОЧКИ ДЕЙСТВИЙ ===== */
        
        .action-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(136, 200, 188, 0.15);
            transition: all 0.2s ease;
            cursor: pointer;
        }
        
        .action-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
            border-color: rgba(136, 200, 188, 0.3);
        }
        
        /* ===== МЕТКИ СТАТУСА ===== */
        
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
        
        /* ===== УЛУЧШЕННЫЕ КАРТОЧКИ ===== */
        
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
        
        .booking-card h3, .booking-card h4 {
            margin-top: 0;
            color: #2d5a4f;
        }
        
        /* ===== WELCOME HEADER ===== */
        
        .welcome-header {
            background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%);
            color: white;
            padding: 2.5rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 8px 24px rgba(136, 200, 188, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .welcome-header h1 { 
            font-weight: 700;
            letter-spacing: -0.02em;
            margin-bottom: 0.5rem;
            font-size: 2rem;
        }
        
        .welcome-header p { 
            opacity: 0.95;
            font-weight: 400;
            font-size: 1.1rem;
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
        
        /* ===== ЗАГОЛОВКИ РАЗДЕЛОВ ===== */
        
        h4 {
            color: #2d5a4f;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }
        
        /* ===== РАЗДЕЛИТЕЛИ ===== */
        
        hr {
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(136, 200, 188, 0.3), transparent);
            margin: 2rem 0;
        }
        
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
        
   /* ===== RESPONSIVE ===== */

        @media (max-width: 768px) {
            /* Сбалансированные колонки на мобильных */
            [data-testid="column"] {
                width: 100% !important;
                flex: 100% !important;
            }
            
            /* Информационная панель на мобильных */
            .info-section {
                padding: 1.25rem !important;
                margin-bottom: 1rem !important;
            }
            
            .info-section h4 {
                font-size: 1.05rem !important;
                margin-bottom: 1rem !important;
            }
            
            .info-content {
                font-size: 0.92rem !important;
            }
            
            .info-icon {
                font-size: 1.15rem !important;
            }
            
            /* Make large headings more compact on phones */
            h1 {
                font-size: 1.25rem;
                margin-bottom: 0.4rem;
            }

            h2 {
                font-size: 1.05rem;
                margin-bottom: 0.35rem;
            }

            h3 {
                font-size: 0.98rem;
                margin-bottom: 0.3rem;
            }

            h4 {
                font-size: 0.95rem;
                margin-bottom: 0.25rem;
            }

            /* Tighter welcome header on small screens */
            .welcome-header {
                padding: 1.2rem 1rem;
            }

            .welcome-header h1 {
                font-size: 1.6rem; /* slightly larger than page h1 but reduced from desktop */
            }

            .welcome-header p {
                font-size: 1rem;
            }

            /* Reduce inner paddings for cards to avoid bulky look */
            .booking-card, .action-card {
                padding: 1rem;
            }

            .stTabs [data-baseweb="tab"] {
                padding: 0.5rem 1rem;
                font-size: 0.85rem;
            }

            /* Stronger overrides targeting Streamlit's emotion-generated selectors
               Streamlit can inject rules like `.st-emotion-cache-xxx h1 { font-size: 2.75rem }`.
               These selectors have equal specificity, so we use attribute selectors and
               !important to ensure mobile rules win. */
            [class*="st-emotion-cache"] h1,
            .stMarkdown h1,
            [data-testid="stHeading"] h1 {
                font-size: 1.25rem !important;
                line-height: 1.15 !important;
                margin-bottom: 0.4rem !important;
            }

            [class*="st-emotion-cache"] h2,
            .stMarkdown h2 {
                font-size: 1.05rem !important;
                line-height: 1.12 !important;
                margin-bottom: 0.35rem !important;
            }

            [class*="st-emotion-cache"] h3,
            .stMarkdown h3 {
                font-size: 0.98rem !important;
                line-height: 1.1 !important;
                margin-bottom: 0.3rem !important;
            }

            [class*="st-emotion-cache"] h4,
            .stMarkdown h4 {
                font-size: 0.95rem !important;
                line-height: 1.08 !important;
                margin-bottom: 0.25rem !important;
            }

            /* Ensure welcome-header remains slightly larger but constrained */
            [class*="st-emotion-cache"] .welcome-header h1,
            .welcome-header h1 {
                font-size: 1.6rem !important;
                margin-bottom: 0.35rem !important;
            }

            /* Target Streamlit heading widgets and common telegram/info cards which
               sometimes render very large text — make them compact on mobile */
            [data-testid="stHeading"] h1,
            [data-testid="stHeading"] h2,
            [data-testid="stHeading"] h3,
            [data-testid="stHeading"] h4,
            [class*="st-emotion-cache"] .telegram-disconnected,
            [class*="st-emotion-cache"] .telegram-connected,
            .telegram-disconnected h1,
            .telegram-disconnected h2,
            .telegram-disconnected h3,
            .telegram-connected h1,
            .telegram-connected h2,
            .telegram-connected h3 {
                font-size: 1,08rem !important;
                line-height: 1.08 !important;
                margin-bottom: 0.25rem !important;
            }

            /* Metric-like big values (в карточках статистики) */
            [data-testid="stMetricValue"],
            [class*="st-emotion-cache"] [data-testid="stMetricValue"] {
                font-size: 1.15rem !important;
            }
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
        
        /* ===== САЙДБАР ===== */
         [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.98);
            border-right: 1px solid rgba(0, 0, 0, 0.06);
        }
        
        /* Скрываем пустой сайдбар на публичной странице */
        [data-testid="stSidebar"]:has(> div > div:empty) {
            display: none;
        

        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4 { 
            letter-spacing: -0.01em;
            font-weight: 600;
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