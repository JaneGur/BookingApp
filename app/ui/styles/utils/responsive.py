def get_responsive_styles():
    return """
    @media (max-width: 768px) {
        /* КРИТИЧНО: Убираем лишние wrapper-контейнеры */
        .main .block-container {
            padding: 1rem 0.5rem !important;
            max-width: 100% !important;
        }
        
        /* Убираем огромные вертикальные отступы у вложенных div */
        [data-testid="stVerticalBlock"] > div:not([class]) {
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Компактные колонки */
        [data-testid="column"] {
            width: 100% !important;
            flex: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Убираем padding у wrapper div */
        [data-testid="stVerticalBlock"] > div > div:not([class*="st-"]) {
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Компактные формы */
        [data-testid="stForm"] {
            padding: 0.75rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Компактные expander */
        [data-testid="stExpander"] {
            margin-bottom: 0.5rem !important;
        }
        
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
        
        /* Компактные заголовки */
        h1 {
            font-size: 1.25rem !important;
            margin-bottom: 0.4rem !important;
            padding-top: 0.5rem !important;
        }

        h2 {
            font-size: 1.05rem !important;
            margin-bottom: 0.35rem !important;
            padding-top: 0.4rem !important;
        }

        h3 {
            font-size: 0.98rem !important;
            margin-bottom: 0.3rem !important;
            padding-top: 0.3rem !important;
        }

        h4 {
            font-size: 0.95rem !important;
            margin-bottom: 0.25rem !important;
            padding-top: 0.2rem !important;
        }

        /* Компактный welcome header */
        .welcome-header {
            padding: 1.2rem 1rem !important;
            margin-bottom: 1rem !important;
        }

        .welcome-header h1 {
            font-size: 1.6rem !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .welcome-header p {
            font-size: 1rem !important;
            margin-top: 0.5rem !important;
        }

        /* Компактные карточки */
        .booking-card, .action-card {
            padding: 1rem !important;
            margin-bottom: 0.75rem !important;
        }

        /* Компактные табы */
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 1rem !important;
            font-size: 0.85rem !important;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.25rem !important;
        }

        /* Общие overrides для всех элементов Streamlit */
        [class*="st-emotion-cache"] h1,
        .stMarkdown h1,
        [data-testid="stHeading"] h1 {
            font-size: 1.25rem !important;
            line-height: 1.15 !important;
            margin-bottom: 0.4rem !important;
            padding-top: 0.5rem !important;
        }

        [class*="st-emotion-cache"] h2,
        .stMarkdown h2 {
            font-size: 1.05rem !important;
            line-height: 1.12 !important;
            margin-bottom: 0.35rem !important;
            padding-top: 0.4rem !important;
        }

        [class*="st-emotion-cache"] h3,
        .stMarkdown h3 {
            font-size: 0.98rem !important;
            line-height: 1.1 !important;
            margin-bottom: 0.3rem !important;
            padding-top: 0.3rem !important;
        }

        [class*="st-emotion-cache"] h4,
        .stMarkdown h4 {
            font-size: 0.95rem !important;
            line-height: 1.08 !important;
            margin-bottom: 0.25rem !important;
            padding-top: 0.2rem !important;
        }

        /* Telegram/info карточки */
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
            font-size: 1.08rem !important;
            line-height: 1.08 !important;
            margin-bottom: 0.25rem !important;
        }

        /* Компактные метрики */
        [data-testid="stMetricValue"],
        [class*="st-emotion-cache"] [data-testid="stMetricValue"] {
            font-size: 1.15rem !important;
        }
        
        [data-testid="stMetric"] {
            padding: 0.75rem !important;
        }
        
        /* Убираем избыточные вертикальные отступы */
        .element-container {
            margin-bottom: 0.5rem !important;
        }
        
        /* Компактные кнопки */
        .stButton > button {
            padding: 0.5rem 1rem !important;
            font-size: 0.9rem !important;
        }
        
        /* Компактные inputs */
        .stTextInput > div > div,
        .stTextArea > div > div,
        .stSelectbox > div > div {
            padding: 0.5rem !important;
        }
        
        /* Убираем лишние gap между элементами */
        [data-testid="stVerticalBlock"] {
            gap: 0.5rem !important;
        }
    }
    """