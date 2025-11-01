import streamlit as st
from core.database import db_manager

@st.cache_data(ttl=300, show_spinner=False)
def get_policy_offer_urls():
    """Возвращает (policy_url, offer_url) из таблицы documents. Может вернуть (None, None)."""
    try:
        sb = db_manager.get_client()
        if sb is None:
            return None, None
        resp = sb.table('documents').select('doc_type, url, is_active, updated_at').eq('is_active', True).execute()
        rows = resp.data or []
        def pick(dt):
            docs = [r for r in rows if (r.get('doc_type') == dt and r.get('url'))]
            docs.sort(key=lambda r: r.get('updated_at') or '', reverse=True)
            return docs[0]['url'] if docs else None
        return pick('policy'), pick('offer')
    except Exception:
        return None, None

def render_consent_line():
    policy_url, offer_url = get_policy_offer_urls()
    policy_link = f"[политикой конфиденциальности]({policy_url})" if policy_url else "политикой конфиденциальности"
    offer_link = f"[условиями оферты]({offer_url})" if offer_url else "условиями оферты"
    st.markdown(f"<small>Продолжая, вы соглашаетесь с {offer_link} и {policy_link}.</small>", unsafe_allow_html=True)
