def get_navigation_styles():
    return """
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
    
    /* Сайдбар */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.98);
        border-right: 1px solid rgba(0, 0, 0, 0.06);
    }
    
    /* Скрываем пустой сайдбар на публичной странице */
    [data-testid="stSidebar"]:has(> div > div:empty) {
        display: none;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 { 
        letter-spacing: -0.01em;
        font-weight: 600;
    }
    
    /* Радио навигация (Chip Style) */
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
    """