def get_card_styles():
    return """
    /* Карточки действий с улучшенным дизайном */
    .action-card {
        background: 
            linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(250, 253, 252, 0.95) 100%);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(136, 200, 188, 0.15);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        animation: fadeIn 0.3s ease;
        backdrop-filter: blur(8px);
        box-shadow: 
            0 2px 8px rgba(0, 0, 0, 0.02),
            0 1px 3px rgba(136, 200, 188, 0.05);
        position: relative;
        overflow: hidden;
    }
    
    .action-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #88c8bc, #6ba292);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .action-card:hover {
        transform: translateY(-3px);
        box-shadow: 
            0 8px 20px rgba(0, 0, 0, 0.04),
            0 4px 8px rgba(136, 200, 188, 0.12);
        border-color: rgba(136, 200, 188, 0.3);
    }
    
    .action-card:hover::before {
        opacity: 1;
    }
    
    /* Карточки бронирований */
    .booking-card {
        padding: 2rem;
        border-radius: 20px;
        background: 
            linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(252, 254, 253, 0.95) 100%);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(136, 200, 188, 0.15);
        box-shadow: 
            0 4px 16px rgba(0, 0, 0, 0.03),
            0 2px 6px rgba(136, 200, 188, 0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeIn 0.3s ease;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    /* Тонкий декоративный элемент */
    .booking-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        right: 0;
        width: 120px;
        height: 120px;
        background: radial-gradient(circle, rgba(136, 200, 188, 0.08) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    
    .booking-card:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 8px 24px rgba(0, 0, 0, 0.05),
            0 4px 10px rgba(136, 200, 188, 0.12);
        border-color: rgba(136, 200, 188, 0.25);
    }
    
    .booking-card h3, .booking-card h4 {
        margin-top: 0;
        color: #2d5a4f;
    }
    
    /* Информационные блоки */
    .info-box {
        background: 
            linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 252, 250, 0.95) 100%);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 
            0 4px 16px rgba(0, 0, 0, 0.03),
            0 2px 6px rgba(136, 200, 188, 0.06);
        border: 1px solid rgba(136, 200, 188, 0.12);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        position: relative;
    }
    
    .info-box::before {
        content: '';
        position: absolute;
        top: -1px;
        left: -1px;
        right: -1px;
        bottom: -1px;
        background: linear-gradient(135deg, rgba(136, 200, 188, 0.1), rgba(168, 213, 186, 0.05));
        border-radius: 20px;
        z-index: -1;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .info-box:hover {
        box-shadow: 
            0 6px 20px rgba(0, 0, 0, 0.04),
            0 3px 8px rgba(136, 200, 188, 0.1);
    }
    
    .info-box:hover::before {
        opacity: 1;
    }
    """