def get_card_styles():
    return """
    /* Карточки действий */
    .action-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(136, 200, 188, 0.15);
        transition: all 0.2s ease;
        cursor: pointer;
        animation: fadeIn 0.3s ease;
    }
    
    .action-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        border-color: rgba(136, 200, 188, 0.3);
    }
    
    /* Карточки бронирований */
    .booking-card {
        padding: 2rem;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.95);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(136, 200, 188, 0.15);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
        transition: all 0.25s ease;
        animation: fadeIn 0.3s ease;
    }
    
    .booking-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border-color: rgba(136, 200, 188, 0.25);
    }
    
    .booking-card h3, .booking-card h4 {
        margin-top: 0;
        color: #2d5a4f;
    }
    
    /* Информационные блоки */
    .info-box {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(136, 200, 188, 0.15);
        transition: all 0.2s ease;
    }
    
    .info-box:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    }
    """