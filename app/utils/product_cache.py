import streamlit as st
from typing import Dict, Any
from core.database import db_manager

@st.cache_data(ttl=300, show_spinner=False)
def get_product_map() -> Dict[int, Dict[str, Any]]:
    """Кэшированный мэп продуктов: id -> {name, price_rub}.
    TTL 5 минут, чтобы снизить число запросов.
    """
    sb = db_manager.get_client()
    if sb is None:
        return {}
    try:
        resp = sb.table('products').select('id, name, price_rub').eq('is_active', True).execute()
        rows = resp.data or []
        return {r['id']: {'name': r.get('name'), 'price_rub': r.get('price_rub')} for r in rows if r.get('id') is not None}
    except Exception:
        return {}

def get_product_name(product_id: int) -> str | None:
    m = get_product_map()
    info = m.get(product_id)
    return info.get('name') if info else None

def get_product_price(product_id: int) -> float | None:
    m = get_product_map()
    info = m.get(product_id)
    return info.get('price_rub') if info else None
