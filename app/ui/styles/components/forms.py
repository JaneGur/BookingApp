def get_form_styles():
    return """
    /* Поля ввода */
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
    
    /* Алерты */
    .stAlert {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    """