def get_layout_styles():
    return """
    /* Метрики с улучшенным дизайном */
    [data-testid="stMetric"] {
        background: 
            linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(252, 254, 253, 0.95) 100%);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 
            0 2px 10px rgba(0, 0, 0, 0.03),
            0 1px 3px rgba(136, 200, 188, 0.08);
        border: 1px solid rgba(136, 200, 188, 0.15);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(8px);
        position: relative;
        overflow: hidden;
    }
    
    /* Декоративный элемент для метрик */
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 80px;
        height: 80px;
        background: radial-gradient(circle, rgba(136, 200, 188, 0.06) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    
    [data-testid="stMetric"]:hover {
        box-shadow: 
            0 4px 16px rgba(0, 0, 0, 0.05),
            0 2px 6px rgba(136, 200, 188, 0.12);
        transform: translateY(-2px);
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
        position: relative;
        padding-left: 1rem;
    }
    
    h4::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 60%;
        background: linear-gradient(180deg, #88c8bc, #6ba292);
        border-radius: 2px;
    }
    
    /* Разделители с градиентом */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(
            90deg, 
            transparent, 
            rgba(136, 200, 188, 0.3) 20%, 
            rgba(136, 200, 188, 0.5) 50%,
            rgba(136, 200, 188, 0.3) 80%,
            transparent
        );
        margin: 2rem 0;
        position: relative;
    }
    
    hr::before {
        content: '';
        position: absolute;
        top: -3px;
        left: 50%;
        transform: translateX(-50%);
        width: 8px;
        height: 8px;
        background: linear-gradient(135deg, #88c8bc, #6ba292);
        border-radius: 50%;
        box-shadow: 0 0 0 3px rgba(136, 200, 188, 0.1);
    }
    """