def get_button_styles():
    return """
    /* Основные кнопки */
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
    
    /* Вторичные кнопки */
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
    """