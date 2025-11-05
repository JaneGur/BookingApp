import streamlit as st
from core.database import db_manager
from utils.datetime_helpers import now_msk

def render_products_tab():
    
    """Управление продуктами для оплаты"""
    st.markdown("""
    <h3 style="color: #225c52; font-size: 1.4rem; font-weight: 600; 
         margin-bottom: 1.25rem; padding-bottom: 0.75rem; 
         border-bottom: 2px solid rgba(136, 200, 188, 0.2);">
        💳 Продукты оплаты
    </h3>
    """, unsafe_allow_html=True)

    sb_read = db_manager.get_client()
    sb_write = db_manager.get_service_client()
    if sb_read is None:
        st.error("❌ Нет подключения к базе данных")
        return

    # Загрузка продуктов
    products = []
    try:
        resp = sb_read.table('products').select("*").order('sort_order').order('created_at').execute()
        products = resp.data or []
    except Exception as e:
        st.error(f"❌ Таблица products не найдена или недоступна. Ошибка: {e}")
        with st.expander("📄 Инструкция по созданию таблицы products", expanded=False):
            st.code(
                """
                CREATE TABLE IF NOT EXISTS products (
                  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                  name TEXT NOT NULL,
                  sku TEXT UNIQUE,
                  description TEXT,
                  price_rub NUMERIC(10,2) NOT NULL DEFAULT 0,
                  is_active BOOLEAN NOT NULL DEFAULT TRUE,
                  is_package BOOLEAN NOT NULL DEFAULT FALSE,
                  sessions_count INTEGER,
                  sort_order INTEGER NOT NULL DEFAULT 100,
                  is_featured BOOLEAN NOT NULL DEFAULT FALSE,
                  created_at TIMESTAMPTZ DEFAULT NOW(),
                  updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS products_active_idx ON products(is_active);
                CREATE INDEX IF NOT EXISTS products_sort_idx ON products(sort_order);
                -- Дополнительно (опционально): разрешить только один продукт со значением is_featured = TRUE
                -- Этот индекс гарантирует, что только одна строка может иметь is_featured = TRUE
                CREATE UNIQUE INDEX IF NOT EXISTS one_featured_true_idx ON products((is_featured)) WHERE is_featured;
                """,
                language="sql"
            )
        return

    # Форма создания/редактирования
    st.markdown("#### ➕ Создать/изменить продукт")
    with st.form("product_form"):
        col_a, col_b = st.columns([2, 1])
        with col_a:
            name = st.text_input("Название *", placeholder="Первая консультация")
            sku = st.text_input("SKU", placeholder="FIRST_SESSION")
            description = st.text_area("Описание", placeholder="Краткое описание продукта", height=90)
        with col_b:
            price = st.number_input("Цена, ₽", min_value=0.0, step=100.0, value=0.0, format="%0.2f")
            is_package = st.checkbox("Пакет", value=False)
            sessions = st.number_input("Кол-во сессий (для пакета)", min_value=1, step=1, value=1, disabled=not is_package)
            is_active = st.checkbox("Активен", value=True)
            sort_order = st.number_input("Порядок", min_value=1, step=1, value=100)
            is_featured = st.checkbox("Для главного экрана", value=False)

        col_save, col_cancel = st.columns([1,1])
        with col_save:
            submit = st.form_submit_button("💾 Сохранить продукт", use_container_width=True)
        with col_cancel:
            reset = st.form_submit_button("↩️ Сброс", use_container_width=True)

        if submit:
            if not name or price <= 0:
                st.error("❌ Укажите название и положительную цену")
            else:
                payload = {
                    'name': name.strip(),
                    'sku': sku.strip().upper() if sku else None,
                    'description': description.strip() if description else None,
                    'price_rub': float(price),
                    'is_active': is_active,
                    'is_package': is_package,
                    'sessions_count': int(sessions) if is_package else None,
                    'sort_order': int(sort_order),
                    'is_featured': bool(is_featured)
                }
                try:
                    # Если помечаем как featured — снимаем флаг со всех остальных
                    if payload.get('is_featured'):
                        try:
                            (sb_write or sb_read).table('products').update({'is_featured': False}).neq('id', -1).execute()
                        except Exception:
                            pass
                    (sb_write or sb_read).table('products').insert(payload).execute()
                    st.success("✅ Продукт создан")
                    st.rerun()
                except Exception as e:
                    # Попытка как upsert по SKU, если есть
                    try:
                        if payload['sku']:
                            if payload.get('is_featured'):
                                try:
                                    (sb_write or sb_read).table('products').update({'is_featured': False}).neq('sku', payload['sku']).execute()
                                except Exception:
                                    pass
                            (sb_write or sb_read).table('products').upsert(payload, on_conflict='sku').execute()
                            st.success("✅ Продукт сохранён (upsert)")
                            st.rerun()
                        else:
                            raise e
                    except Exception as e2:
                        # Повторяем без поля is_featured, если столбца ещё нет
                        try:
                            payload_fallback = dict(payload)
                            payload_fallback.pop('is_featured', None)
                            if payload_fallback.get('sku'):
                                (sb_write or sb_read).table('products').upsert(payload_fallback, on_conflict='sku').execute()
                            else:
                                (sb_write or sb_read).table('products').insert(payload_fallback).execute()
                            st.warning("⚠️ Столбец is_featured отсутствует. Добавьте его по инструкции SQL выше.")
                            st.success("✅ Продукт сохранён")
                            st.rerun()
                        except Exception as e3:
                            st.error(f"❌ Ошибка сохранения: {e3}")

    st.markdown("---")
    st.markdown("#### 📋 Список продуктов")
    if not products:
        st.info("Пока нет продуктов. Создайте первый выше.")
        return

    for p in products:
        with st.expander(f"{('🟢' if p.get('is_active') else '⚪️')} {p.get('name')} — {p.get('price_rub')} ₽", expanded=False):
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            with c1:
                st.write(f"SKU: {p.get('sku') or '—'}")
                st.write(f"Описание: {p.get('description') or '—'}")
                st.write(f"Пакет: {'Да' if p.get('is_package') else 'Нет'}")
                if p.get('is_package'):
                    st.write(f"Сессий: {p.get('sessions_count')}")
                st.write(f"Для главного экрана: {'Да' if p.get('is_featured') else 'Нет'}")
            with c2:
                new_price = st.number_input("Цена, ₽", min_value=0.0, step=100.0, value=float(p.get('price_rub') or 0), key=f"price_{p['id']}")
                new_active = st.checkbox("Активен", value=bool(p.get('is_active')), key=f"active_{p['id']}")
                new_order = st.number_input("Порядок", min_value=1, step=1, value=int(p.get('sort_order') or 100), key=f"order_{p['id']}")
            with c3:
                rename = st.text_input("Название", value=p.get('name') or '', key=f"name_{p['id']}")
                resku = st.text_input("SKU", value=p.get('sku') or '', key=f"sku_{p['id']}")
                repack = st.checkbox("Пакет", value=bool(p.get('is_package')), key=f"pkg_{p['id']}")
                recnt = st.number_input("Сессий", min_value=1, step=1, value=int(p.get('sessions_count') or 1), key=f"cnt_{p['id']}", disabled=not repack)
                new_featured = st.checkbox("Для главного экрана", value=bool(p.get('is_featured')), key=f"feat_{p['id']}")
            with c4:
                if st.button("💾 Обновить", key=f"upd_{p['id']}", use_container_width=True):
                    upd = {
                        'name': rename.strip() or p.get('name'),
                        'sku': (resku.strip().upper() if resku else None),
                        'price_rub': float(new_price),
                        'is_active': new_active,
                        'sort_order': int(new_order),
                        'is_package': repack,
                        'sessions_count': (int(recnt) if repack else None),
                        'is_featured': bool(new_featured),
                        'updated_at': now_msk().isoformat()
                    }
                    try:
                        # Если данный продукт становится featured — снимем флаг у остальных
                        if upd.get('is_featured'):
                            try:
                                sb_write.table('products').update({'is_featured': False}).neq('id', p['id']).execute()
                            except Exception:
                                pass
                        sb_write.table('products').update(upd).eq('id', p['id']).execute()
                        st.success("✅ Обновлено")
                        st.rerun()
                    except Exception as e:
                        # Повтор без is_featured, если столбец отсутствует
                        try:
                            upd_fallback = dict(upd)
                            upd_fallback.pop('is_featured', None)
                            sb_write.table('products').update(upd_fallback).eq('id', p['id']).execute()
                            st.warning("⚠️ Столбец is_featured отсутствует. Добавьте его по инструкции SQL выше.")
                            st.success("✅ Обновлено")
                            st.rerun()
                        except Exception as e2:
                            st.error(f"❌ Ошибка обновления: {e2}")
                if st.button("🗑️ Удалить", key=f"del_{p['id']}", use_container_width=True):
                    try:
                        sb_write.table('products').delete().eq('id', p['id']).execute()
                        st.success("✅ Удалено")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Ошибка удаления: {e}")