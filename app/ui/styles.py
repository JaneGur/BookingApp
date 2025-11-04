from .styles import load_all_styles, load_public_styles, load_admin_styles

# Для обратной совместимости
def load_custom_css():
    """Основная функция загрузки стилей"""
    load_all_styles()