from .admin import render_admin_panel
from .client_cabinet import render_client_cabinet
from .public import render_public_booking
from .auth_forms import render_auth_forms

__all__ = [
    'render_admin_panel',
    'render_client_cabinet', 
    'render_public_booking',
    'render_auth_forms'
]