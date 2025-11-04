def get_layout_styles():
    return """
    /* Метрики */
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
    
    /* Заголовки разделов */
    h4 {
        color: #2d5a4f;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Разделители */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(136, 200, 188, 0.3), transparent);
        margin: 2rem 0;
    }
    """