def get_responsive_styles():
    return """
    @media (max-width: 768px) {
        /* КРИТИЧНО: Убираем ВСЕ лишние wrapper-контейнеры */
        .main .block-container {
            padding: 0.5rem !important;
            max-width: 100% !important;
        }
        
        /* ЛИЧНЫЙ КАБИНЕТ - КОМПАКТНАЯ КАРТОЧКА */
        /* Карточка личного кабинета - ОБЯЗАТЕЛЬНЫЙ PADDING */
        div[style*="linear-gradient"][style*="#88c8bc"],
        div[style*="background: linear-gradient"][style*="88c8bc"] {
            padding: 1.25rem 1rem !important;
            margin: 0.75rem 0 1.25rem 0 !important;
            border-radius: 14px !important;
        }
        
        /* Заголовки внутри карточек - с padding */
        div[style*="linear-gradient"] h1,
        div[style*="linear-gradient(135deg"] h1 {
            font-size: 1.4rem !important;
            margin: 0 0 0.5rem 0 !important;
            padding: 0 !important;
            line-height: 1.35 !important;
        }
        
        div[style*="linear-gradient"] p,
        div[style*="linear-gradient(135deg"] p {
            font-size: 0.95rem !important;
            margin: 0.5rem 0 0 0 !important;
            padding: 0 !important;
        }
        
        /* Компактные метрики - НО С PADDING */
        [data-testid="stMetric"] {
            padding: 0.75rem 0.65rem !important;
            margin: 0.5rem 0 !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.1rem !important;
            font-weight: 600 !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
        }
        
        /* ОЧЕНЬ КОМПАКТНЫЕ ТАБЫ */
        .stTabs {
            padding: 0.5rem !important;
            margin-bottom: 1.25rem !important;
            border-radius: 12px !important;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.25rem !important;
            flex-wrap: wrap !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.6rem 0.9rem !important;
            font-size: 0.85rem !important;
            min-height: auto !important;
            white-space: nowrap !important;
            border-radius: 8px !important;
        }
        
        /* Уменьшаем иконки в табах */
        .stTabs [data-baseweb="tab"] span {
            font-size: 0.7rem !important;
        }
        
        /* КАРТОЧКИ КОНСУЛЬТАЦИЙ - КОМПАКТНЫЕ НО С PADDING */
        div[style*="rgba(255, 255, 255, 0.95)"][style*="padding"],
        div[style*="background: rgba(255, 255, 255, 0.95)"] {
            padding: 1rem !important;
            margin: 0.75rem 0 !important;
            border-radius: 12px !important;
        }
        
        /* Заголовки в карточках */
        div[style*="rgba(255, 255, 255, 0.95)"] p[style*="font-size: 1.2rem"],
        div[style*="background: rgba(255, 255, 255, 0.95)"] p[style*="font-size: 1.2rem"] {
            font-size: 1.05rem !important;
            line-height: 1.3 !important;
        }
        
        div[style*="rgba(255, 255, 255, 0.95)"] p[style*="font-size: 1rem"],
        div[style*="background: rgba(255, 255, 255, 0.95)"] p[style*="font-size: 1rem"] {
            font-size: 0.9rem !important;
            line-height: 1.4 !important;
        }
        
        /* Статусные бейджи */
        span[style*="padding: 4px 12px"] {
            padding: 3px 8px !important;
            font-size: 0.75rem !important;
        }
        
        /* Кнопки в карточках - УДОБНЫЕ ДЛЯ ТАПА */
        [data-testid="column"] .stButton > button {
            padding: 0.65rem 0.9rem !important;
            font-size: 0.9rem !important;
            min-height: 40px !important;
        }
        
        /* Все обычные кнопки */
        .stButton > button {
            padding: 0.7rem 1.2rem !important;
            font-size: 0.95rem !important;
            min-height: 44px !important;
        }
        
        /* АГРЕССИВНОЕ УМЕНЬШЕНИЕ ОТСТУПОВ */
        [data-testid="stVerticalBlock"] > div:not(:first-child) {
            margin-top: 0.5rem !important;
        }
        
        /* Убираем лишние отступы у hr */
        hr {
            margin: 1rem 0 !important;
        }
        
        /* Компактные h3 заголовки */
        h3[style*="color: #225c52"] {
            font-size: 1.05rem !important;
            margin-bottom: 0.75rem !important;
            padding-bottom: 0.5rem !important;
        }
        
        /* Быстрые действия - в две колонки */
        [data-testid="column"]:has(.stButton) {
            min-width: calc(50% - 0.25rem) !important;
            flex: 0 0 calc(50% - 0.25rem) !important;
        }
        
        /* Формы - компактнее */
        [data-testid="stForm"] {
            padding: 1rem !important;
            margin-bottom: 1rem !important;
        }
        
        /* Text inputs */
        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox select {
            font-size: 0.9rem !important;
            padding: 0.5rem !important;
        }
        
        /* КРИТИЧНО: Убираем огромные отступы ТОЛЬКО у wrapper-ов */
        /* НЕ ТРОГАЕМ контент внутри карточек! */
        .main > div:not([data-testid]):not([class*="st-"]):not([style*="gradient"]) {
            margin: 0 !important;
        }
        
        /* УДАЛЯЕМ АГРЕССИВНОЕ ОБНУЛЕНИЕ - оно убивает padding везде */
        /* .main div:not([class]):not([data-testid]) {
            padding: 0 !important;
            margin: 0 !important;
        } */
        
        /* Убираем отступы у вертикальных блоков */
        [data-testid="stVerticalBlock"],
        [data-testid="stVerticalBlock"] > div,
        [data-testid="stVerticalBlock"] > div > div,
        [data-testid="stVerticalBlock"] > div > div > div {
            padding: 0 !important;
            margin: 0 !important;
            gap: 0.5rem !important;
        }
        
        /* Убираем отступы у горизонтальных блоков */
        [data-testid="stHorizontalBlock"],
        [data-testid="stHorizontalBlock"] > div,
        [data-testid="stHorizontalBlock"] > div > div,
        [data-testid="stHorizontalBlock"] > div > div > div {
            padding: 0 !important;
            margin: 0 !important;
            gap: 0.5rem !important;
        }
        
        /* Компактные колонки */
        [data-testid="column"],
        [data-testid="column"] > div,
        [data-testid="column"] > div > div {
            width: 100% !important;
            flex: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
            min-width: 100% !important;
        }
        
        /* Убираем лишние gap между элементами */
        [data-testid="stVerticalBlock"] {
            gap: 0.5rem !important;
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
        
        /* Компактные кнопки - УДОБНЫЕ */
        .stButton > button {
            padding: 0.7rem 1.2rem !important;
            font-size: 0.95rem !important;
            min-height: 44px !important;
        }
        
        /* Компактные inputs */
        .stTextInput > div > div,
        .stTextArea > div > div,
        .stSelectbox > div > div {
            padding: 0.65rem !important;
            font-size: 0.95rem !important;
        }
        
        /* БОЛЬШЕ НЕ ОБНУЛЯЕМ padding у styled элементов */
        /* Они теперь управляются выше через специфичные селекторы */
        
        /* Форсируем компактный режим для всех внутренних элементов */
        .main * {
            box-sizing: border-box !important;
        }
        
        /* Убираем любые минимальные ширины */
        [data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"],
        [data-testid="column"] {
            min-width: unset !important;
        }
    }
    """