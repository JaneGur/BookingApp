def get_form_styles():
    return """
    /* Поля ввода с улучшенным дизайном */
    .stTextInput input, .stTextArea textarea, 
    .stSelectbox select, .stDateInput input, 
    .stTimeInput input {
        border-radius: 12px !important;
        border: 1.5px solid rgba(136, 200, 188, 0.25) !important;
        background: rgba(255, 255, 255, 0.95) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(4px);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus, 
    .stSelectbox select:focus, .stDateInput input:focus, 
    .stTimeInput input:focus {
        outline: none !important;
        border-color: #88c8bc !important;
        box-shadow: 
            0 0 0 3px rgba(136, 200, 188, 0.1),
            0 2px 8px rgba(136, 200, 188, 0.15);
        background: rgba(255, 255, 255, 1) !important;
    }
    
    /* Контейнеры форм */
    [data-testid="stForm"] {
        background: 
            linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(250, 253, 252, 0.9) 100%);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(136, 200, 188, 0.15);
        box-shadow: 
            0 4px 16px rgba(0, 0, 0, 0.03),
            0 2px 6px rgba(136, 200, 188, 0.08);
        backdrop-filter: blur(10px);
    }
    
    /* Алерты с улучшенным дизайном */
    .stAlert {
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(8px);
        box-shadow: 
            0 2px 8px rgba(0, 0, 0, 0.04),
            0 1px 3px rgba(0, 0, 0, 0.02);
    }
    
    /* Success alerts */
    [data-testid="stAlert"] [data-baseweb="notification"][kind="success"] {
        background: linear-gradient(135deg, rgba(236, 253, 245, 0.95) 0%, rgba(209, 250, 229, 0.95) 100%);
        border-left: 4px solid #10b981;
    }
    
    /* Info alerts */
    [data-testid="stAlert"] [data-baseweb="notification"][kind="info"] {
        background: linear-gradient(135deg, rgba(239, 246, 255, 0.95) 0%, rgba(219, 234, 254, 0.95) 100%);
        border-left: 4px solid #3b82f6;
    }
    
    /* Warning alerts */
    [data-testid="stAlert"] [data-baseweb="notification"][kind="warning"] {
        background: linear-gradient(135deg, rgba(255, 251, 235, 0.95) 0%, rgba(254, 243, 199, 0.95) 100%);
        border-left: 4px solid #f59e0b;
    }
    
    /* Error alerts */
    [data-testid="stAlert"] [data-baseweb="notification"][kind="error"] {
        background: linear-gradient(135deg, rgba(254, 242, 242, 0.95) 0%, rgba(254, 226, 226, 0.95) 100%);
        border-left: 4px solid #ef4444;
    }
    """