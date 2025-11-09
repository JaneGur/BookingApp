def get_responsive_styles():
    return """
    @media (max-width: 768px) {
        /* ===== КРИТИЧНО: УБИВАЕМ ПУСТЫЕ ПРОСТРАНСТВА ===== */
        
        /* Убираем ВСЕ лишние контейнеры Streamlit */
        .main .block-container,
        .main .block-container > div,
        .main .block-container > div > div,
        .main .block-container > div > div > div {
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Основной контейнер - только минимальный padding */
        .main .block-container {
            padding: 0.75rem !important;
        }
        
        /* УБИВАЕМ все вертикальные и горизонтальные блоки-обертки */
        [data-testid="stVerticalBlock"],
        [data-testid="stVerticalBlock"] > div,
        [data-testid="stVerticalBlock"] > div > div,
        [data-testid="stHorizontalBlock"],
        [data-testid="stHorizontalBlock"] > div,
        [data-testid="stHorizontalBlock"] > div > div {
            padding: 0 !important;
            margin: 0 !important;
            gap: 0.5rem !important;
        }
        
        /* Колонки - убираем padding */
        [data-testid="column"],
        [data-testid="column"] > div,
        [data-testid="column"] > div > div {
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Element containers - минимальные отступы */
        .element-container {
            margin: 0 0 0.75rem 0 !important;
        }
        
        .element-container:last-child {
            margin-bottom: 0 !important;
        }
        
        /* ===== КОНТЕНТНЫЕ БЛОКИ (только они имеют padding) ===== */
        
        /* Градиентные карточки - ВАЖНЫЙ КОНТЕНТ */
        div[style*="linear-gradient"][style*="#88c8bc"] {
            padding: 1.25rem 1rem !important;
            margin: 0 0 1rem 0 !important;
            border-radius: 14px !important;
        }
        
        div[style*="linear-gradient"] h1 {
            font-size: 1.4rem !important;
            margin: 0 0 0.35rem 0 !important;
            line-height: 1.25 !important;
        }
        
        div[style*="linear-gradient"] p {
            font-size: 0.9rem !important;
            margin: 0 !important;
        }
        
        /* Белые карточки консультаций */
        div[style*="rgba(255, 255, 255, 0.95)"] {
            padding: 1rem !important;
            margin: 0.75rem 0 !important;
            border-radius: 12px !important;
        }
        
        div[style*="rgba(255, 255, 255, 0.95)"] p {
            font-size: 0.9rem !important;
            line-height: 1.4 !important;
            margin: 0.25rem 0 !important;
        }
        
        /* Статусные карточки с border-left */
        div[style*="border-left: 4px solid"] {
            padding: 0.85rem 1rem !important;
            margin: 0.5rem 0 !important;
            border-radius: 10px !important;
        }
        
        /* Метрики - КОМПАКТНО */
        [data-testid="stMetric"] {
            padding: 0.75rem !important;
            margin: 0 0 0.5rem 0 !important;
            border-radius: 12px !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.3rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
        }
        
        /* ===== ТАБЫ - УЛЬТРА КОМПАКТНО ===== */
        .stTabs {
            padding: 0.4rem !important;
            margin: 0 0 1rem 0 !important;
            border-radius: 12px !important;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.3rem !important;
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            scrollbar-width: none !important;
        }
        
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
            display: none !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.6rem 0.85rem !important;
            font-size: 0.85rem !important;
            min-height: 38px !important;
            border-radius: 8px !important;
            flex-shrink: 0 !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            padding: 0.75rem 0 0 0 !important;
        }
        
        /* ===== КНОПКИ - УДОБНЫЕ ДЛЯ ТАПА ===== */
        .stButton > button {
            padding: 0.75rem 1rem !important;
            font-size: 0.95rem !important;
            min-height: 46px !important;
            border-radius: 10px !important;
            margin: 0 !important;
        }
        
        /* Кнопки в колонках */
        [data-testid="column"] .stButton {
            margin: 0 !important;
        }
        
        [data-testid="column"] .stButton > button {
            padding: 0.65rem 0.85rem !important;
            font-size: 0.9rem !important;
            min-height: 42px !important;
        }
        
        /* ===== ПОЛЯ ВВОДА - КОМПАКТНО ===== */
        .stTextInput,
        .stTextArea,
        .stSelectbox,
        .stDateInput,
        .stTimeInput {
            margin: 0 0 0.5rem 0 !important;
        }
        
        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox select,
        .stDateInput input,
        .stTimeInput input {
            font-size: 0.95rem !important;
            padding: 0.65rem !important;
            border-radius: 8px !important;
        }
        
        .stTextInput label,
        .stTextArea label,
        .stSelectbox label {
            font-size: 0.85rem !important;
            margin-bottom: 0.25rem !important;
        }
        
        /* ===== ФОРМЫ - БЕЗ ЛИШНЕГО ===== */
        [data-testid="stForm"] {
            padding: 1rem !important;
            margin: 0 0 1rem 0 !important;
            border-radius: 12px !important;
        }
        
        /* ===== ЗАГОЛОВКИ - КОМПАКТНО ===== */
        h1 {
            font-size: 1.35rem !important;
            margin: 0 0 0.5rem 0 !important;
            line-height: 1.2 !important;
        }
        
        h2 {
            font-size: 1.2rem !important;
            margin: 0 0 0.4rem 0 !important;
            line-height: 1.2 !important;
        }
        
        h3 {
            font-size: 1.1rem !important;
            margin: 0 0 0.4rem 0 !important;
            line-height: 1.2 !important;
        }
        
        h4 {
            font-size: 1rem !important;
            margin: 0 0 0.3rem 0 !important;
            line-height: 1.2 !important;
        }
        
        h3[style*="color: #225c52"] {
            font-size: 1.15rem !important;
            margin: 0 0 0.75rem 0 !important;
            padding-bottom: 0.5rem !important;
        }
        
        /* ===== КОЛОНКИ - НА УЗКИХ ЭКРАНАХ В СТОЛБИК ===== */
        @media (max-width: 480px) {
            [data-testid="column"] {
                min-width: 100% !important;
                flex: 0 0 100% !important;
                margin-bottom: 0.5rem !important;
            }
            
            [data-testid="column"]:last-child {
                margin-bottom: 0 !important;
            }
        }
        
        /* ===== РАЗДЕЛИТЕЛИ - МИНИМАЛЬНЫЕ ===== */
        hr {
            margin: 1rem 0 !important;
            opacity: 0.6 !important;
        }
        
        /* ===== ИНФОРМАЦИОННАЯ ПАНЕЛЬ ===== */
        .info-section {
            padding: 1rem !important;
            margin: 0 0 0.75rem 0 !important;
            border-radius: 12px !important;
        }
        
        .info-section h4 {
            font-size: 1rem !important;
            margin: 0 0 0.75rem 0 !important;
        }
        
        .info-content {
            font-size: 0.9rem !important;
            line-height: 1.5 !important;
        }
        
        .info-icon {
            font-size: 1.1rem !important;
            margin-right: 0.6rem !important;
        }
        
        .info-item {
            margin-bottom: 0.75rem !important;
        }
        
        .info-item:last-child {
            margin-bottom: 0 !important;
        }
        
        /* Sticky панель - отключаем на мобильных */
        .info-panel-wrapper {
            position: static !important;
            max-height: none !important;
        }
        
        /* ===== TELEGRAM БЛОКИ - КОМПАКТНО ===== */
        .telegram-connected,
        .telegram-disconnected {
            padding: 1rem !important;
            margin: 0.75rem 0 !important;
            border-radius: 12px !important;
        }
        
        .telegram-connected h3,
        .telegram-disconnected h3 {
            font-size: 1.05rem !important;
            margin: 0 0 0.5rem 0 !important;
        }
        
        .telegram-connected p,
        .telegram-disconnected p {
            font-size: 0.9rem !important;
            margin: 0.25rem 0 !important;
        }
        
        /* ===== АЛЕРТЫ - КОМПАКТНО ===== */
        .stAlert,
        [data-testid="stAlert"] {
            padding: 0.75rem !important;
            margin: 0.5rem 0 !important;
            border-radius: 10px !important;
            font-size: 0.9rem !important;
        }
        
        /* ===== EXPANDER - КОМПАКТНО ===== */
        [data-testid="stExpander"] {
            margin: 0 0 0.75rem 0 !important;
        }
        
        [data-testid="stExpander"] summary {
            padding: 0.75rem !important;
            font-size: 0.95rem !important;
        }
        
        [data-testid="stExpander"] > div {
            padding: 0.75rem !important;
        }
        
        /* ===== ПРОГРЕСС ИНДИКАТОР ===== */
        .progress-mobile {
            display: block !important;
            margin: 0 0 1rem 0 !important;
        }
        
        .progress-desktop {
            display: none !important;
        }
        
        .mobile-step-info {
            padding: 0.85rem !important;
            border-radius: 10px !important;
        }
        
        .progress-bar-container {
            height: 4px !important;
            margin-bottom: 0.6rem !important;
        }
        
        /* ===== КАРТОЧКИ ЗАПИСЕЙ - КОМПАКТНО ===== */
        .booking-card,
        .action-card {
            padding: 1rem !important;
            margin: 0 0 0.75rem 0 !important;
            border-radius: 12px !important;
        }
        
        /* ===== ТИПОГРАФИКА - КОМПАКТНАЯ ===== */
        body,
        .stMarkdown,
        .stMarkdown p {
            font-size: 0.95rem !important;
            line-height: 1.5 !important;
        }
        
        p {
            margin: 0 0 0.5rem 0 !important;
        }
        
        /* ===== СТАТУСНЫЕ БЕЙДЖИ ===== */
        span[style*="padding: 4px 12px"],
        span[style*="padding: 0.25rem"] {
            padding: 0.3rem 0.65rem !important;
            font-size: 0.8rem !important;
            border-radius: 6px !important;
        }
        
        /* ===== УБИРАЕМ ВСЕ ЛИШНИЕ ОТСТУПЫ ===== */
        
        /* Убираем огромные gap у Streamlit */
        [data-testid="stVerticalBlock"] {
            gap: 0.5rem !important;
        }
        
        [data-testid="stHorizontalBlock"] {
            gap: 0.5rem !important;
        }
        
        /* Убираем минимальные высоты */
        [data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"] {
            min-height: 0 !important;
        }
        
        /* Все пустые div убираем */
        .main div:empty {
            display: none !important;
        }
        
        /* Убираем лишние wrapper-ы */
        .main > div > div > div:not([class]):not([data-testid]) {
            padding: 0 !important;
            margin: 0 !important;
        }
    }
    """