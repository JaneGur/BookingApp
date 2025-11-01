import streamlit as st
from config.constants import STATUS_DISPLAY
from services.booking_service import BookingService
from services.notification_service import NotificationService
from utils.product_cache import get_product_map
from utils.first_session_cache import has_paid_first_consultation_cached

def render_booking_card(booking: dict, show_actions: bool = True, on_delete_callback=None):
    """Отрисовка карточки записи"""
    status_info = STATUS_DISPLAY.get(booking['status'], STATUS_DISPLAY['confirmed'])
    
    unique_key = f"delete_{booking['booking_date']}_{booking['booking_time']}_{booking['id']}"
    
    with st.container():
        col1, col2 = st.columns([4, 1]) if show_actions else st.columns([1])
        
        with col1:
            st.markdown(f"**{status_info['emoji']} {booking['booking_time']} - {booking['client_name']}**")
            st.text(f"📱 {booking['client_phone']}")
            
            if booking.get('client_email'):
                st.text(f"📧 {booking['client_email']}")
                
            if booking.get('client_telegram'):
                st.text(f"💬 {booking['client_telegram']}")
                
            if booking.get('notes'):
                st.text(f"💭 {booking['notes']}")

            # Продукт и сумма (если указаны)
            try:
                pid = booking.get('product_id') if isinstance(booking, dict) else None
                amt = booking.get('amount') if isinstance(booking, dict) else None
                if pid is not None or amt is not None:
                    prod_map = get_product_map()
                    pname = prod_map.get(pid, {}).get('name') if pid is not None else None
                    pname_disp = pname or (f"ID {pid}" if pid is not None else "Не выбран")
                    st.text(f"🧾 Продукт: {pname_disp}{(f', Сумма: {amt} ₽' if amt is not None else '')}")
            except Exception:
                pass

            # Если это заказ в ожидании оплаты — позволим выбрать продукт
            if str(booking.get('status')) == 'pending_payment':
                try:
                    pmap = get_product_map()
                    # Фильтрация первой консультации, если уже была оплачена у клиента
                    phone = booking.get('client_phone', '')
                    has_paid_first = has_paid_first_consultation_cached(phone) if phone else False
                    def is_first_product(name: str, sku: str | None = None) -> bool:
                        sku_u = (sku or '').upper()
                        nm = (name or '').lower()
                        return sku_u == 'FIRST_SESSION' or ('перва' in nm and 'консультац' in nm)
                    # Собираем список из продуктов кэша (активные)
                    # Так как кэш не хранит sku, фильтрация по названию
                    items = [(pid, info.get('name'), info.get('price_rub')) for pid, info in pmap.items()]
                    if has_paid_first:
                        items = [it for it in items if not is_first_product(it[1])]
                    if items:
                        labels = [f"{name} — {price} ₽" for _, name, price in items]
                        current_pid = booking.get('product_id')
                        try:
                            default_idx = next((i for i, (pid, _, _) in enumerate(items) if pid == current_pid), 0)
                        except Exception:
                            default_idx = 0
                        choice_idx = st.selectbox("Выберите продукт", options=list(range(len(items))), index=default_idx, format_func=lambda i: labels[i], key=f"adm_choice_{booking['id']}")
                        if choice_idx is not None:
                            sel_pid = items[choice_idx][0]
                            if sel_pid != current_pid:
                                st.info(f"🧾 Текущий выбор (не сохранён): {items[choice_idx][1]} — {items[choice_idx][2]} ₽")
                        if st.button("💾 Сохранить продукт", key=f"adm_save_prod_{booking['id']}", use_container_width=False):
                            try:
                                pid_sel, _name, price = items[choice_idx]
                                bs = BookingService()
                                ok = bs.set_booking_payment_info(booking['id'], pid_sel, float(price or 0))
                                if ok:
                                    st.success("✅ Сохранено")
                                    st.rerun()
                                else:
                                    st.error("❌ Нельзя выбрать этот продукт для клиента")
                            except Exception as e:
                                st.error(f"❌ Ошибка сохранения: {e}")
                    else:
                        st.warning("Нет доступных продуктов для выбора")
                except Exception:
                    pass
            
            st.markdown(f"**Статус:** <span style='color: {status_info['color']};'>{status_info['text']}</span>", 
                       unsafe_allow_html=True)
        
        if show_actions and col2:
            with col2:
                bs = BookingService()
                # Действия для заказов в ожидании оплаты
                if booking.get('status') == 'pending_payment':
                    if st.button("💳 Оплачено", key=f"paid_{unique_key}", width='stretch'):
                        ok, msg = bs.mark_booking_paid(booking['id'])
                        if ok:
                            # Уведомим администратора в Telegram
                            try:
                                ns = NotificationService()
                                prod_map = get_product_map()
                                pid = booking.get('product_id')
                                pname = prod_map.get(pid, {}).get('name') if pid is not None else None
                                amount = booking.get('amount')
                                date_txt = booking.get('booking_date','')
                                time_txt = booking.get('booking_time','')
                                name = booking.get('client_name','Клиент')
                                phone = booking.get('client_phone','')
                                text = (
                                    f"💳 <b>ОПЛАТА ПОЛУЧЕНА</b>\n\n"
                                    f"👤 <b>Клиент:</b> {name}\n"
                                    f"📱 <b>Телефон:</b> <code>{phone}</code>\n"
                                    f"🧾 <b>Продукт:</b> {pname or '—'}{(f' — {amount} ₽' if amount is not None else '')}\n"
                                    f"📅 <b>Дата:</b> {date_txt}\n🕐 <b>Время:</b> {time_txt}"
                                )
                                ns.bot.send_to_admin(text)
                            except Exception:
                                pass
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    if st.button("❌ Отменить", key=f"cancel_{unique_key}", width='stretch'):
                        ok, msg = bs.update_booking_status(booking['id'], 'cancelled')
                        if ok:
                            st.success("✅ Отменено")
                            st.rerun()
                        else:
                            st.error(msg)
                # Напоминания для оплаченных (confirmed/completed)
                elif booking.get('status') in ('confirmed', 'completed'):
                    st.caption("Напоминания")
                    try:
                        ns = NotificationService()
                        if st.button("🔔 Напомнить админу", key=f"rem_admin_{unique_key}", width='stretch'):
                            if ns.bot.notify_reminder_admin(booking):
                                st.success("✅ Напоминание админу отправлено")
                            else:
                                st.error("❌ Не удалось отправить администратору")
                        chat_id = ns.get_client_telegram_chat_id(booking.get('client_phone',''))
                        disabled = not bool(chat_id)
                        label = "🔔 Напомнить клиенту" + (" (Telegram не подключен)" if disabled else "")
                        if st.button(label, key=f"rem_client_{unique_key}", disabled=disabled, width='stretch'):
                            if ns.bot.notify_reminder_client(chat_id, booking):
                                st.success("✅ Напоминание клиенту отправлено")
                            else:
                                st.error("❌ Не удалось отправить клиенту")
                    except Exception:
                        pass
                # Удаление (общая кнопка)
                if str(booking.get('status')) not in ('confirmed', 'completed'):
                    if st.button("🗑️ Удалить", key=unique_key, width='stretch'):
                        if bs.delete_booking(booking['id']):
                            st.success("✅ Удалено!")
                            if on_delete_callback:
                                on_delete_callback()
                            st.rerun()
        
        st.markdown("---")