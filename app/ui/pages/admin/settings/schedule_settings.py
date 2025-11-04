import streamlit as st
from datetime import datetime as dt, timedelta
from services.settings_service import SettingsService
from utils.datetime_helpers import now_msk

def render_schedule_settings(settings_service):
    """Настройки расписания"""
    st.markdown("#### 📅 Настройки расписания")
    
    settings = settings_service.get_settings()
    if settings:
        col1, col2, col3 = st.columns(3)
        with col1:
            work_start = st.time_input("🕐 Начало рабочего дня", 
                                     value=dt.strptime(settings.work_start, '%H:%M').time())
        with col2:
            work_end = st.time_input("🕐 Конец рабочего дня", 
                                   value=dt.strptime(settings.work_end, '%H:%M').time())
        with col3:
            session_duration = st.number_input("⏱️ Длительность сессии (мин)", 
                                              min_value=15, max_value=180, 
                                              value=settings.session_duration, step=15)
        # Подсказка: последняя сессия начинается не позже (work_end - duration)
        try:
            today = dt.combine(now_msk().date(), work_end)
            last_start_dt = today - timedelta(minutes=int(session_duration))
            st.caption(f"Последняя сессия должна начинаться не позже: {last_start_dt.strftime('%H:%M')}")
            # Валидация: интервал дня должен быть >= длительности
            start_dt = dt.combine(now_msk().date(), work_start)
            if last_start_dt < start_dt:
                st.error("Длительность сессии больше рабочего интервала. Уменьшите длительность или сдвиньте границы дня.")
                save_allowed = False
            else:
                save_allowed = True
        except Exception:
            save_allowed = True
        
        if st.button("💾 Сохранить настройки расписания", width='stretch', disabled=not save_allowed):
            update_data = {
                'work_start': work_start.strftime('%H:%M'),
                'work_end': work_end.strftime('%H:%M'),
                'session_duration': session_duration
            }
            
            if settings_service.update_settings(update_data):
                st.success("✅ Настройки расписания сохранены!")
                st.rerun()
            else:
                st.error("❌ Ошибка сохранения настроек расписания")