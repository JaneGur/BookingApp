def get_public_page_styles():
    return """
    /* Welcome Header */
    .welcome-header {
        background: linear-gradient(135deg, #88c8bc 0%, #6ba292 100%);
        color: white;
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 24px rgba(136, 200, 188, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .welcome-header h1 { 
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
        font-size: 2rem;
    }
    
    .welcome-header p { 
        opacity: 0.95;
        font-weight: 400;
        font-size: 1.1rem;
    }
    """