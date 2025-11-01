import streamlit as st
from datetime import datetime, timedelta
from config.constants import BOOKING_RULES
from services.booking_service import BookingService
from services.client_service import ClientService
from services.notification_service import NotificationService
from ui.components import render_time_slots, render_info_panel
from utils.validators import validate_phone, validate_email
from utils.product_cache import get_product_map
from utils.first_session_cache import has_paid_first_consultation_cached
from utils.docs import render_consent_line
from utils.datetime_helpers import now_msk

def render_public_booking():
    """Отрисовка публичной страницы записи"""
    st.title("🌿 Запись на консультацию")
    
    booking_service = BookingService()
    client_service = ClientService()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 📅 Новая запись")
        st.caption("Всё время — по Москве (MSK)")
        # Выбор даты
        min_date = now_msk().date()
        max_date = min_date + timedelta(days=BOOKING_RULES["MAX_DAYS_AHEAD"])
        
        selected_date = st.date_input("Дата консультации", min_value=min_date, 
                                      max_value=max_date, value=min_date, format="DD.MM.YYYY")
        
        # Получаем слоты
        available_slots = booking_service.get_available_slots(str(selected_date))
        selected_time = render_time_slots(available_slots, "guest_slot")
        
        if selected_time:
            st.success(f"✅ Выбрано: **{selected_date.strftime('%d.%m.%Y')}** в **{selected_time}**")
            
            st.markdown("#### 👤 Ваши данные")
            with st.form("booking_form"):
                # Плашка с продуктом по умолчанию (только в форме заказа)
                try:
                    from core.database import db_manager
                    supabase = db_manager.get_client()
                    products_all = supabase.table('products').select('id,name,price_rub,is_featured,is_active').eq('is_active', True).order('sort_order').execute().data or []
                except Exception:
                    products_all = []
                featured = [p for p in products_all if p.get('is_featured')]
                chosen_disp = (featured[0] if featured else (products_all[0] if products_all else None))
                if chosen_disp:
                    st.success(f"💳 Будет оформлен продукт: {chosen_disp.get('name')} — {chosen_disp.get('price_rub')} ₽")
                col_a, col_b = st.columns(2)
                with col_a:
                    client_name = st.text_input("👤 Имя *", placeholder="Иван Иванов")
                    client_email = st.text_input("📧 Email", placeholder="example@mail.com")
                    client_chat_id = st.text_input("💬 ID Telegram для уведомлений", 
                                                 placeholder="123456789 (опционально)",
                                                 help="Чтобы получать уведомления о записи и напоминания")
                with col_b:
                    client_phone = st.text_input("📱 Телефон *", placeholder="+7 (999) 123-45-67")
                    client_telegram = st.text_input("💬 Telegram username", placeholder="@username")
                
                notes = st.text_area("💭 Комментарий (необязательно)", height=80)
                submit = st.form_submit_button("✅ Создать заказ", width='stretch')
                render_consent_line()
                
                if submit:
                    # Валидация
                    if not client_name or not client_phone:
                        st.error("❌ Заполните имя и телефон")
                    else:
                        phone_valid, phone_msg = validate_phone(client_phone)
                        if not phone_valid:
                            st.error(phone_msg)
                        else:
                            if client_email:
                                email_valid, email_msg = validate_email(client_email)
                                if not email_valid:
                                    st.error(email_msg)
                                    return
                            
                            # Создаем заказ (а не подтвержденную запись)
                            booking_data = {
                                'client_name': client_name,
                                'client_phone': client_phone,
                                'client_email': client_email,
                                'client_telegram': client_telegram,
                                'booking_date': str(selected_date),
                                'booking_time': selected_time,
                                'notes': notes,
                                'telegram_chat_id': client_chat_id,
                                'status': 'pending_payment'
                            }
                            # Создаём заказ
                            prior_df = booking_service.get_client_bookings(client_phone)
                            success, message = booking_service.create_booking(booking_data)
                            if success:
                                # Обновим/создадим профиль и авторизуем клиента в кабинете
                                try:
                                    client_service.upsert_profile(client_phone, client_name.strip(), client_email.strip(), client_telegram.strip())
                                except Exception:
                                    pass
                                st.session_state.client_logged_in = True
                                st.session_state.client_phone = client_phone
                                st.session_state.client_name = client_name
                                st.session_state.client_nav = "🏠 Главная"
                                # Флаг, чтобы при первом заходе в кабинет остаться на Главной
                                st.session_state.client_go_home_once = True
                                # Флаг для одноразового баннера об успешно созданном заказе
                                st.session_state.client_pending_created_ctx = {
                                    'date': str(selected_date),
                                    'time': selected_time
                                }
                                st.success("✅ Заказ создан. Перенаправляем в личный кабинет…")
                                st.rerun()
                                # Ниже код не выполнится из-за rerun
                                st.balloons()
                                st.info("🟡 Заказ создан и ожидает оплаты. После оплаты он будет подтверждён.")
                                # Автоприсвоение дефолтного продукта (первый активный по sort_order)
                                try:
                                    from core.database import db_manager
                                    supabase = db_manager.get_client()
                                    products_all = supabase.table('products').select('*').eq('is_active', True).order('sort_order').execute().data or []
                                except Exception:
                                    products_all = []
                                # Фильтрация первой консультации, если уже была оплачена для этого номера
                                has_paid_first = booking_service.has_paid_first_consultation(client_phone)
                                def is_first_product(p):
                                    sku = (p.get('sku') or '').upper()
                                    name = (p.get('name') or '').lower()
                                    return sku == 'FIRST_SESSION' or ('перва' in name and 'консультац' in name)
                                filtered = [p for p in (products_all or []) if not (has_paid_first and is_first_product(p))]
                                # Выбираем продукт для главного экрана
                                featured = [p for p in filtered if p.get('is_featured')]
                                chosen = (featured[0] if featured else (filtered[0] if filtered else None))
                                st.session_state._guest_pending_payment_ctx = {
                                    'date': str(selected_date),
                                    'time': selected_time,
                                    'phone': client_phone,
                                    'product_id': (chosen.get('id') if chosen else None)
                                }
                                # Сохраняем выбранный (featured) продукт в заказе сразу
                                try:
                                    row = booking_service.get_booking_by_datetime(client_phone, str(selected_date), selected_time)
                                    if row and chosen:
                                        booking_service.set_booking_payment_info(row['id'], chosen.get('id'), float(chosen.get('price_rub') or 0))
                                except Exception:
                                    pass
                                st.rerun()
                            else:
                                st.error(message)
    
            # Блок оплаты (вне формы)
            ctx = st.session_state.get('_guest_pending_payment_ctx')
            if ctx and ctx.get('date') == str(selected_date) and ctx.get('time') == selected_time:
                st.markdown("---")
                st.markdown("#### 💳 Оплата заказа")
                # Показываем назначенный продукт (поменять нельзя)
                try:
                    from core.database import db_manager
                    supabase = db_manager.get_client()
                    row = booking_service.get_booking_by_datetime(ctx['phone'], ctx['date'], ctx['time'])
                    if row:
                        pid = row.get('product_id')
                        amt = row.get('amount')
                        pmap = get_product_map()
                        pname = pmap.get(pid, {}).get('name') if pid is not None else None
                        pname_disp = pname or (f"ID {pid}" if pid is not None else '—')
                        st.success(f"🧾 Продукт для заказа: {pname_disp}{f' — {amt} ₽' if amt is not None else ''}")
                except Exception:
                    pass
                col_pay1, col_pay2 = st.columns([1,1])
                with col_pay1:
                    if st.button("Перейти к оплате", type="primary", width='stretch'):
                        st.info("Оплата будет подключена позже. Сейчас это заглушка.")
                with col_pay2:
                    if st.button("Оплатить позже", width='stretch'):
                        st.session_state._guest_pending_payment_ctx = None
                        st.rerun()
                render_consent_line()

    with col2:
        render_info_panel()