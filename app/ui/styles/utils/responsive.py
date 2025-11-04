def get_responsive_styles():
    return """
    @media (max-width: 768px) {
        [data-testid="column"] {
            width: 100% !important;
            flex: 100% !important;
        }
        
        .info-section {
            padding: 1.25rem !important;
            margin-bottom: 1rem !important;
        }
        
        .info-section h4 {
            font-size: 1.05rem !important;
            margin-bottom: 1rem !important;
        }
        
        .info-content {
            font-size: 0.92rem !important;
        }
        
        .info-icon {
            font-size: 1.15rem !important;
        }
        
        /* Make large headings more compact on phones */
        h1 {
            font-size: 1.25rem;
            margin-bottom: 0.4rem;
        }

        h2 {
            font-size: 1.05rem;
            margin-bottom: 0.35rem;
        }

        h3 {
            font-size: 0.98rem;
            margin-bottom: 0.3rem;
        }

        h4 {
            font-size: 0.95rem;
            margin-bottom: 0.25rem;
        }

        /* Tighter welcome header on small screens */
        .welcome-header {
            padding: 1.2rem 1rem;
        }

        .welcome-header h1 {
            font-size: 1.6rem;
        }

        .welcome-header p {
            font-size: 1rem;
        }

        /* Reduce inner paddings for cards */
        .booking-card, .action-card {
            padding: 1rem;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 1rem;
            font-size: 0.85rem;
        }

        /* Mobile heading overrides */
        [class*="st-emotion-cache"] h1,
        .stMarkdown h1,
        [data-testid="stHeading"] h1 {
            font-size: 1.25rem !important;
            line-height: 1.15 !important;
            margin-bottom: 0.4rem !important;
        }

        [class*="st-emotion-cache"] h2,
        .stMarkdown h2 {
            font-size: 1.05rem !important;
            line-height: 1.12 !important;
            margin-bottom: 0.35rem !important;
        }

        [class*="st-emotion-cache"] h3,
        .stMarkdown h3 {
            font-size: 0.98rem !important;
            line-height: 1.1 !important;
            margin-bottom: 0.3rem !important;
        }

        [class*="st-emotion-cache"] h4,
        .stMarkdown h4 {
            font-size: 0.95rem !important;
            line-height: 1.08 !important;
            margin-bottom: 0.25rem !important;
        }

        /* Welcome header mobile */
        [class*="st-emotion-cache"] .welcome-header h1,
        .welcome-header h1 {
            font-size: 1.6rem !important;
            margin-bottom: 0.35rem !important;
        }

        /* Telegram and info cards */
        [data-testid="stHeading"] h1,
        [data-testid="stHeading"] h2,
        [data-testid="stHeading"] h3,
        [data-testid="stHeading"] h4,
        [class*="st-emotion-cache"] .telegram-disconnected,
        [class*="st-emotion-cache"] .telegram-connected,
        .telegram-disconnected h1,
        .telegram-disconnected h2,
        .telegram-disconnected h3,
        .telegram-connected h1,
        .telegram-connected h2,
        .telegram-connected h3 {
            font-size: 1.08rem !important;
            line-height: 1.08 !important;
            margin-bottom: 0.25rem !important;
        }

        /* Metric values */
        [data-testid="stMetricValue"],
        [class*="st-emotion-cache"] [data-testid="stMetricValue"] {
            font-size: 1.15rem !important;
        }
    }
    """