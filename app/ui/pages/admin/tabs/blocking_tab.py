import streamlit as st
from core.database import db_manager
from utils.datetime_helpers import now_msk
from utils.formatters import format_date
from datetime import datetime

def render_blocking_tab():
    """Вкладка блокировок"""
    st.markdown("### 🚫 Управление блокировками")

    sb_read = db_manager.get_client()
    sb_write = db_manager.get_service_client()
    if sb_read is None:
        st.error("❌ Нет подключения к базе данных")
        return

    # Форма блокировки целого дня
    render_day_blocking_form(sb_read, sb_write)
    
    st.markdown("---")

    # Форма блокировки конкретного слота
    render_time_blocking_form(sb_read, sb_write)

    st.markdown("---")

    # Список существующих блокировок
    render_blocking_list(sb_read, sb_write)

def render_day_blocking_form(sb_read, sb_write):
    """Форма блокировки дня"""
    with st.form("block_day_form"):
        st.markdown("#### 📅 Заблокировать день")
        block_day_date = st.date_input(
            "Дата для блокировки",
            min_value=now_msk().date(),
            key="block_day_date",
        )
        reason_day = st.text_input("💬 Причина (необязательно)", placeholder="Отпуск, выходной, командировка…", key="block_day_reason")
        col1, col2 = st.columns([1, 1])
        with col1:
            submit_block_day = st.form_submit_button("🚫 Заблокировать день", use_container_width=True)
        with col2:
            cancel_block_day = st.form_submit_button("❌ Отмена", use_container_width=True)

        if submit_block_day:
            try:
                # Проверка дубликата
                existing = sb_read.table('blocked_slots')\
                    .select('id')\
                    .eq('block_date', str(block_day_date))\
                    .is_('block_time', None)\
                    .execute()
                if existing.data:
                    st.warning("⚠️ Такой день уже заблокирован")
                else:
                    payload = {
                        'block_date': str(block_day_date),
                        'block_time': None
                    }
                    if reason_day:
                        payload['reason'] = reason_day
                    try:
                        (sb_write or sb_read).table('blocked_slots').insert(payload).execute()
                    except Exception:
                        # Повтор без reason, если в БД нет такого столбца
                        (sb_write or sb_read).table('blocked_slots').insert({
                            'block_date': str(block_day_date),
                            'block_time': None
                        }).execute()
                    st.success("✅ День заблокирован")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Ошибка блокировки дня: {e}")

def render_time_blocking_form(sb_read, sb_write):
    """Форма блокировки временного слота"""
    with st.form("block_time_form"):
        st.markdown("#### 🕐 Заблокировать временной слот")
        col_dt1, col_dt2 = st.columns([1, 1])
        with col_dt1:
            block_time_date = st.date_input(
                "Дата",
                min_value=now_msk().date(),
                key="block_time_date",
            )
        with col_dt2:
            default_time = datetime.strptime("09:00", "%H:%M").time()
            block_time_time = st.time_input("Время", value=default_time, key="block_time_time")
        reason_time = st.text_input("💬 Причина (необязательно)", placeholder="Окно занято, личное дело…", key="block_time_reason")

        col_bt1, col_bt2 = st.columns([1, 1])
        with col_bt1:
            submit_block_time = st.form_submit_button("🚫 Заблокировать слот", use_container_width=True)
        with col_bt2:
            cancel_block_time = st.form_submit_button("❌ Отмена", use_container_width=True)

        if submit_block_time:
            try:
                time_str = block_time_time.strftime('%H:%M')
                # Проверка дубликата
                existing = sb_read.table('blocked_slots')\
                    .select('id')\
                    .eq('block_date', str(block_time_date))\
                    .eq('block_time', time_str)\
                    .execute()
                if existing.data:
                    st.warning("⚠️ Такой слот уже заблокирован")
                else:
                    payload = {
                        'block_date': str(block_time_date),
                        'block_time': time_str
                    }
                    if reason_time:
                        payload['reason'] = reason_time
                    try:
                        (sb_write or sb_read).table('blocked_slots').insert(payload).execute()
                    except Exception:
                        (sb_write or sb_read).table('blocked_slots').insert({
                            'block_date': str(block_time_date),
                            'block_time': time_str
                        }).execute()
                    st.success("✅ Слот заблокирован")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Ошибка блокировки слота: {e}")

def render_blocking_list(sb_read, sb_write):
    """Список блокировок"""
    st.markdown("#### 📋 Текущие блокировки")
    try:
        resp = sb_read.table('blocked_slots').select('*').order('block_date').order('block_time', nullsfirst=True).execute()
        blocks = resp.data or []
    except Exception as e:
        blocks = []
        st.error(f"❌ Ошибка получения блокировок: {e}")

    # Фильтруем прошлые блокировки
    today_str = str(now_msk().date())
    blocks = [b for b in blocks if b.get('block_date') >= today_str]

    # Разделяем на блокировки дней и слотов
    day_blocks = [b for b in blocks if b.get('block_time') in (None, '')]
    time_blocks = [b for b in blocks if b.get('block_time') not in (None, '')]

    # Блокированные дни
    st.markdown("##### 📅 Заблокированные дни")
    if day_blocks:
        for b in day_blocks:
            col_d1, col_d2 = st.columns([3, 1])
            with col_d1:
                date_txt = format_date(b.get('block_date', ''))
                reason = b.get('reason')
                st.write(f"{date_txt}{' — ' + reason if reason else ''}")
            with col_d2:
                if st.button("🗑️ Удалить", key=f"del_day_{b['id']}", use_container_width=True):
                    try:
                        # Сохраняем данные для Undo
                        st.session_state.last_deleted_block = b
                        (sb_write or sb_read).table('blocked_slots').delete().eq('id', b['id']).execute()
                        undo_col1, undo_col2 = st.columns([3,1])
                        with undo_col1:
                            st.success("✅ Удалено. Можно отменить действие ниже.")
                        with undo_col2:
                            if st.button("↩️ Undo", key=f"undo_day_{b['id']}", use_container_width=True):
                                payload = {
                                    'block_date': b.get('block_date'),
                                    'block_time': None
                                }
                                if b.get('reason'):
                                    payload['reason'] = b.get('reason')
                                try:
                                    (sb_write or sb_read).table('blocked_slots').insert(payload).execute()
                                except Exception:
                                    (sb_write or sb_read).table('blocked_slots').insert({
                                        'block_date': b.get('block_date'),
                                        'block_time': None
                                    }).execute()
                                st.success("↩️ Восстановлено")
                                st.rerun()
                    except Exception as e:
                        st.error(f"❌ Ошибка удаления: {e}")
    else:
        st.info("Нет заблокированных дней")

    st.markdown("##### 🕐 Заблокированные слоты")
    if time_blocks:
        for b in time_blocks:
            col_t1, col_t2, col_t3 = st.columns([2, 1, 1])
            with col_t1:
                date_str = format_date(b.get('block_date', ''))
                time_str = b.get('block_time', '')
                reason = b.get('reason')
                st.write(f"{date_str} — {time_str}{' — ' + reason if reason else ''}")
            with col_t2:
                st.empty()
            with col_t3:
                if st.button("🗑️ Удалить", key=f"del_time_{b['id']}", use_container_width=True):
                    try:
                        st.session_state.last_deleted_block = b
                        (sb_write or sb_read).table('blocked_slots').delete().eq('id', b['id']).execute()
                        undo_col1, undo_col2 = st.columns([3,1])
                        with undo_col1:
                            st.success("✅ Удалено. Можно отменить действие ниже.")
                        with undo_col2:
                            if st.button("↩️ Undo", key=f"undo_time_{b['id']}", use_container_width=True):
                                payload = {
                                    'block_date': b.get('block_date'),
                                    'block_time': b.get('block_time')
                                }
                                if b.get('reason'):
                                    payload['reason'] = b.get('reason')
                                try:
                                    (sb_write or sb_read).table('blocked_slots').insert(payload).execute()
                                except Exception:
                                    (sb_write or sb_read).table('blocked_slots').insert({
                                        'block_date': b.get('block_date'),
                                        'block_time': b.get('block_time')
                                    }).execute()
                                st.success("↩️ Восстановлено")
                                st.rerun()
                    except Exception as e:
                        st.error(f"❌ Ошибка удаления: {e}")