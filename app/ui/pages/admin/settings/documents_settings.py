import streamlit as st
import uuid
from core.database import db_manager
from utils.datetime_helpers import now_msk
from utils.formatters import format_date

def render_documents_settings():
    """Управление документами"""
    st.markdown("#### 📄 Управление документами")
    
    sb_read = db_manager.get_client()
    sb_write = db_manager.get_service_client()
    if sb_read is None:
        st.error("❌ Нет подключения к базе данных")
        return
    
    # Форма загрузки документа
    render_document_upload_form(sb_write, sb_read)
    
    st.markdown("---")
    st.markdown("##### 📚 Список документов")
    
    render_documents_list(sb_read, sb_write)

def render_document_upload_form(sb_write, sb_read):
    """Форма загрузки документа"""
    st.markdown("##### ⬆️ Загрузить документ")
    with st.form("upload_doc_form"):
        colu1, colu2 = st.columns([2,1])
        with colu1:
            title = st.text_input("Название документа *", placeholder="Политика конфиденциальности")
        with colu2:
            doc_type_map = {
                "policy": "📄 Политика",
                "offer": "📝 Оферта", 
                "instruction": "📋 Инструкция",
                "other": "📎 Другое"
            }
            doc_type = st.selectbox("Тип", list(doc_type_map.keys()), 
                                  format_func=lambda x: doc_type_map[x], index=0)
        
        file = st.file_uploader("Файл *", type=["pdf", "doc", "docx", "txt", "rtf"], 
                               accept_multiple_files=False,
                               help="Поддерживаемые форматы: PDF, DOC, DOCX, TXT, RTF")
        
        up_submit = st.form_submit_button("📤 Загрузить документ", use_container_width=True)
    
    if up_submit:
        if not file or not title:
            st.error("❌ Укажите название и выберите файл")
        else:
            ext = (file.name.split(".")[-1] or "bin").lower()
            key = f"{uuid.uuid4().hex}.{ext}"
            try:
                bucket = sb_write.storage.from_("public_docs") if sb_write else None
                if bucket is None:
                    raise Exception("service client is not configured")
                bucket.upload(key, file.getvalue(), {"content_type": (file.type or "application/octet-stream"), "upsert": "true"})
                public_url = bucket.get_public_url(key)
            except Exception as e:
                st.error(f"❌ Хранилище недоступно или не создано: {e}")
                with st.expander("📄 Инструкция по созданию bucket public_docs", expanded=False):
                    st.code(
                        """
                        -- Выполните в Supabase SQL (Storage):
                        -- В разделе Storage создайте bucket с именем public_docs и включите Public.
                        -- Затем перезапустите приложение.
                        """,
                        language="sql"
                    )
                public_url = None
            
            if public_url:
                try:
                    (sb_write or sb_read).table('documents').insert({
                        'title': title.strip(),
                        'doc_type': doc_type,
                        'filename': file.name,
                        'storage_key': key,
                        'url': public_url,
                        'is_active': True,
                        'created_at': now_msk().isoformat(),
                        'updated_at': now_msk().isoformat()
                    }).execute()
                    st.success("✅ Документ загружен")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Ошибка записи в таблицу documents: {e}")
                    with st.expander("📄 Инструкция по созданию таблицы documents", expanded=False):
                        st.code(
                            """
                            CREATE TABLE IF NOT EXISTS documents (
                              id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                              title TEXT NOT NULL,
                              doc_type TEXT,
                              filename TEXT,
                              storage_key TEXT,
                              url TEXT,
                              is_active BOOLEAN DEFAULT TRUE,
                              created_at TIMESTAMPTZ DEFAULT NOW(),
                              updated_at TIMESTAMPTZ DEFAULT NOW()
                            );
                            CREATE INDEX IF NOT EXISTS documents_active_idx ON documents(is_active);
                            """,
                            language="sql"
                        )

def render_documents_list(sb_read, sb_write):
    """Список документов"""
    try:
        rows = sb_read.table('documents').select('*').order('created_at', desc=True).execute().data or []
    except Exception as e:
        rows = []
        st.error(f"❌ Не удалось получить список документов: {e}")
    
    if not rows:
        st.info("📭 Документы отсутствуют")
        return
    
    doc_type_map = {
        "policy": "📄 Политика",
        "offer": "📝 Оферта", 
        "instruction": "📋 Инструкция",
        "other": "📎 Другое"
    }
    
    for d in rows:
        doc_type_display = doc_type_map.get(d.get('doc_type', 'other'), "📎 Другое")
        with st.expander(f"{doc_type_display} — {d.get('title')}", expanded=False):
            col_d1, col_d2 = st.columns([3, 1])
            
            with col_d1:
                st.write(f"**Файл:** {d.get('filename', '—')}")
                if d.get('created_at'):
                    created_date = format_date(d['created_at'][:10]) if 'T' in d['created_at'] else format_date(d['created_at'])
                    st.caption(f"📅 Загружен: {created_date}")
                
                if d.get('url'):
                    st.link_button("🔗 Открыть документ", url=d['url'], use_container_width=True)
            
            with col_d2:
                new_active = st.checkbox("Активен", value=bool(d.get('is_active')), 
                                       key=f"doc_active_{d['id']}")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💾 Сохранить", key=f"doc_save_{d['id']}", use_container_width=True):
                        try:
                            (sb_write or sb_read).table('documents').update({
                                'is_active': new_active, 
                                'updated_at': now_msk().isoformat()
                            }).eq('id', d['id']).execute()
                            st.success("✅ Сохранено")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Ошибка сохранения: {e}")
                
                with col_btn2:
                    if st.button("🗑️ Удалить", key=f"doc_del_{d['id']}", use_container_width=True):
                        try:
                            # Пытаемся удалить файл из хранилища
                            if d.get('storage_key'):
                                try:
                                    (sb_write or sb_read).storage.from_("public_docs").remove([d['storage_key']])
                                except Exception:
                                    pass
                            (sb_write or sb_read).table('documents').delete().eq('id', d['id']).execute()
                            st.success("✅ Удалено")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Ошибка удаления: {e}")