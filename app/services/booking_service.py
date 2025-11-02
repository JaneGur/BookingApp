import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from models.booking import Booking
from core.database import db_manager
from config.constants import BOOKING_RULES
from utils.validators import normalize_phone, hash_password
from utils.datetime_helpers import now_msk, combine_msk

class BookingService:
    
    def __init__(self):
        # Разделяем клиентов: чтение через anon, запись через service role
        self.sb_read = db_manager.get_client()
        self.sb_write = db_manager.get_service_client() or self.sb_read
    
    def create_booking(self, booking_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Создание новой записи"""
        try:
            phone_hash = hash_password(normalize_phone(booking_data['client_phone']))
            
            response = self.sb_write.table('bookings').insert({
                'client_name': booking_data['client_name'],
                'client_phone': booking_data['client_phone'],
                'client_email': booking_data.get('client_email'),
                'client_telegram': booking_data.get('client_telegram'),
                'booking_date': booking_data['booking_date'],
                'booking_time': booking_data['booking_time'],
                'notes': booking_data.get('notes'),
                'phone_hash': phone_hash,
                'status': booking_data.get('status', 'confirmed'),
                'telegram_chat_id': booking_data.get('telegram_chat_id')
            }).execute()
            
            if response.data:
                return True, "✅ Запись успешно создана"
            return False, "❌ Ошибка при создании записи"
            
        except Exception as e:
            if "duplicate key" in str(e) or "unique constraint" in str(e):
                return False, "❌ Это время уже занято"
            return False, f"❌ Ошибка: {str(e)}"
    
    def create_booking_by_admin(self, booking_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Создание записи администратором"""
        try:
            phone_hash = hash_password(normalize_phone(booking_data['client_phone']))
            
            response = self.sb_write.table('bookings').insert({
                'client_name': booking_data['client_name'],
                'client_phone': booking_data['client_phone'],
                'client_email': booking_data.get('client_email'),
                'client_telegram': booking_data.get('client_telegram'),
                'booking_date': booking_data['booking_date'],
                'booking_time': booking_data['booking_time'],
                'notes': booking_data.get('notes'),
                'phone_hash': phone_hash,
                'status': 'confirmed'
            }).execute()
            
            if response.data:
                try:
                    from services.notification_service import NotificationService
                    ns = NotificationService()
                    chat_id = ns.get_client_telegram_chat_id(booking_data['client_phone'])
                    if chat_id:
                        ns.bot.schedule_reminder({
                            'client_name': booking_data.get('client_name'),
                            'client_phone': booking_data.get('client_phone'),
                            'booking_date': booking_data.get('booking_date'),
                            'booking_time': booking_data.get('booking_time'),
                            'notes': booking_data.get('notes')
                        }, chat_id)
                except Exception:
                    pass
                return True, "✅ Запись успешно создана"
            return False, "❌ Ошибка при создании записи"
                
        except Exception as e:
            if "duplicate key" in str(e) or "unique constraint" in str(e):
                return False, "❌ Это время уже занято"
            return False, f"❌ Ошибка: {str(e)}"
    
    def cancel_booking(self, booking_id: int, phone: str) -> Tuple[bool, str]:
        """Отмена записи"""
        try:
            phone_hash = hash_password(normalize_phone(phone))
            
            # Получаем информацию о записи
            response = self.sb_read.table('bookings')\
                .select('*')\
                .eq('id', booking_id)\
                .eq('phone_hash', phone_hash)\
                .execute()
            
            if not response.data:
                return False, "Запись не найдена"
            
            booking = response.data[0]
            
            # Проверяем время до начала
            time_until = self._calculate_time_until(booking['booking_date'], booking['booking_time'])
            min_cancel = BOOKING_RULES["MIN_CANCEL_MINUTES"] * 60
            
            if time_until.total_seconds() < min_cancel:
                return False, f"Отмена возможна не позднее чем за {BOOKING_RULES['MIN_CANCEL_MINUTES']} минут"
            
            # Отменяем запись
            self.sb_write.table('bookings')\
                .update({'status': 'cancelled'})\
                .eq('id', booking_id)\
                .execute()
            # Уведомляем админа и клиента (если подключён)
            try:
                from services.notification_service import NotificationService
                ns = NotificationService()
                # Попробуем получить chat_id из записи или по телефону
                chat_id = booking.get('telegram_chat_id') or ns.get_client_telegram_chat_id(booking.get('client_phone',''))
                try:
                    ns.notify_booking_cancelled(booking, chat_id)
                except Exception:
                    pass
            except Exception:
                pass

            return True, "Запись успешно отменена"
            
        except Exception as e:
            return False, f"❌ Ошибка: {str(e)}"
    
    def delete_booking(self, booking_id: int) -> bool:
        """Удаление записи (для админа)"""
        try:
            self.sb_write.table('bookings').delete().eq('id', booking_id).execute()
            return True
        except Exception as e:
            print(f"❌ Ошибка удаления записи: {e}")
            return False
    
    def get_all_bookings(self, date_from: str = None, date_to: str = None) -> pd.DataFrame:
        """Получение всех записей"""
        try:
            query = self.sb_read.table('bookings').select('*')
            
            if date_from and date_to:
                query = query.gte('booking_date', date_from).lte('booking_date', date_to)
            elif date_from:
                query = query.gte('booking_date', date_from)
            else:
                query = query.order('booking_date', desc=True).order('booking_time', desc=True)
            
            response = query.execute()
            return pd.DataFrame(response.data) if response.data else pd.DataFrame()
        except Exception as e:
            print(f"❌ Ошибка получения записей: {e}")
            return pd.DataFrame()
    
    def get_client_bookings(self, phone: str) -> pd.DataFrame:
        """Получение всех записей клиента"""
        try:
            phone_hash = hash_password(normalize_phone(phone))
            
            response = self.sb_read.table('bookings')\
                .select('*')\
                .eq('phone_hash', phone_hash)\
                .order('booking_date', desc=True)\
                .order('booking_time', desc=True)\
                .execute()
            
            return pd.DataFrame(response.data) if response.data else pd.DataFrame()
        except Exception as e:
            print(f"❌ Ошибка получения записей клиента: {e}")
            return pd.DataFrame()
    
    def get_upcoming_client_booking(self, phone: str) -> Optional[Dict[str, Any]]:
        """Получение ближайшей записи клиента"""
        try:
            phone_hash = hash_password(normalize_phone(phone))
            response = self.sb_read.table('bookings')\
                .select('*')\
                .eq('phone_hash', phone_hash)\
                .eq('status', 'confirmed')\
                .gte('booking_date', now_msk().date().isoformat())\
                .order('booking_date')\
                .order('booking_time')\
                .limit(1)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Ошибка получения ближайшей записи: {e}")
            return None

    def get_latest_pending_booking_for_client(self, phone: str) -> Optional[Dict[str, Any]]:
        """Получить последний заказ в статусе pending_payment (на будущее время)."""
        try:
            phone_hash = hash_password(normalize_phone(phone))
            response = self.sb_read.table('bookings')\
                .select('*')\
                .eq('phone_hash', phone_hash)\
                .eq('status', 'pending_payment')\
                .gte('booking_date', now_msk().date().isoformat())\
                .order('booking_date', desc=True)\
                .order('booking_time', desc=True)\
                .limit(1)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Ошибка получения заказа в ожидании оплаты: {e}")
            return None

    def get_booking_by_datetime(self, phone: str, date_str: str, time_str: str) -> Optional[Dict[str, Any]]:
        """Получить запись по телефону и точной дате/времени (для только что созданной записи)."""
        try:
            phone_hash = hash_password(normalize_phone(phone))
            response = self.sb_read.table('bookings')\
                .select('*')\
                .eq('phone_hash', phone_hash)\
                .eq('booking_date', date_str)\
                .eq('booking_time', time_str)\
                .order('id', desc=True)\
                .limit(1)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Ошибка поиска записи по дате/времени: {e}")
            return None

    def set_booking_payment_info(self, booking_id: int, product_id: Optional[int], amount: Optional[float]) -> bool:
        """Сохранить в брони выбранный продукт и сумму (если есть соответствующие столбцы)."""
        try:
            if product_id is not None:
                booking_resp = self.sb_read.table('bookings')\
                    .select('id, phone_hash')\
                    .eq('id', booking_id)\
                    .limit(1)\
                    .execute()
                booking_row = booking_resp.data[0] if booking_resp.data else None
                if booking_row:
                    try:
                        prod_resp = self.sb_read.table('products')\
                            .select('id, sku, name')\
                            .eq('id', product_id)\
                            .limit(1)\
                            .execute()
                        prod = prod_resp.data[0] if prod_resp.data else None
                    except Exception:
                        prod = None
                    if prod:
                        sku_val = (prod.get('sku') or '').upper()
                        name_val = (prod.get('name') or '').lower()
                        is_first = (sku_val == 'FIRST_SESSION') or ('перва' in name_val and 'консультац' in name_val)
                        if is_first and self.has_paid_first_consultation_by_phone_hash(booking_row['phone_hash']):
                            return False
            payload: Dict[str, Any] = {}
            if product_id is not None:
                payload['product_id'] = product_id
            if amount is not None:
                payload['amount'] = amount
            if not payload:
                return True
            self.sb_write.table('bookings').update(payload).eq('id', booking_id).execute()
            return True
        except Exception as e:
            # Колонки могут отсутствовать — игнорируем, но можно вывести предупреждение в UI
            print(f"⚠️ Не удалось сохранить продукт/сумму в брони: {e}")
            return False

    def mark_booking_paid(self, booking_id: int) -> Tuple[bool, str]:
        """Пометить бронь как оплаченную: status -> confirmed, paid_at = NOW (если колонка есть)."""
        try:
            payload: Dict[str, Any] = {'status': 'confirmed'}
            try:
                payload['paid_at'] = now_msk().isoformat()
            except Exception:
                pass
            self.sb_write.table('bookings').update(payload).eq('id', booking_id).execute()
            # Получаем обновлённую запись и отправляем уведомления
            try:
                resp = self.sb_read.table('bookings').select('*').eq('id', booking_id).limit(1).execute()
                row = resp.data[0] if resp.data else None
                if row:
                    from services.notification_service import NotificationService
                    ns = NotificationService()
                    # Попробуем взять chat_id из записи, если нет — ищем по телефону
                    chat_id = row.get('telegram_chat_id') or ns.get_client_telegram_chat_id(row.get('client_phone',''))
                    try:
                        ns.notify_booking_paid(row, chat_id)
                    except Exception:
                        # как фоллбек — планируем напоминание, если есть chat_id
                        try:
                            if chat_id:
                                ns.bot.schedule_reminder(row, chat_id)
                        except Exception:
                            pass
            except Exception:
                pass
            return True, "✅ Отмечено как оплачено"
        except Exception as e:
            return False, f"❌ Ошибка отметки оплаты: {e}"
    
    def has_active_booking(self, phone: str) -> bool:
        """Проверка наличия активной записи"""
        try:
            phone_hash = hash_password(normalize_phone(phone))
            response = self.sb_read.table('bookings')\
                .select('id', count='exact')\
                .eq('phone_hash', phone_hash)\
                .eq('status', 'confirmed')\
                .gte('booking_date', now_msk().date().isoformat())\
                .execute()
            
            return (response.count or 0) > 0
        except Exception as e:
            print(f"❌ Ошибка проверки активных записей: {e}")
            return False
    
    def get_available_slots(self, date: str) -> List[str]:
        """Получение доступных временных слотов"""
        try:
            from services.settings_service import SettingsService
            settings_service = SettingsService()
            settings = settings_service.get_settings()
            
            if not settings:
                return []
                
            work_start = datetime.strptime(settings.work_start, '%H:%M').time()
            work_end = datetime.strptime(settings.work_end, '%H:%M').time()
            session_duration = settings.session_duration
            
            # Проверка блокировки дня
            blocked_response = self.sb_read.table('blocked_slots')\
                .select('id')\
                .eq('block_date', date)\
                .is_('block_time', None)\
                .execute()
            
            if blocked_response.data:
                return []
            
            # Получаем занятые слоты
            booked_response = self.sb_read.table('bookings')\
                .select('booking_time')\
                .eq('booking_date', date)\
                .neq('status', 'cancelled')\
                .execute()
            
            booked_slots = [item['booking_time'] for item in booked_response.data] if booked_response.data else []
            
            # Получаем заблокированные слоты
            blocked_slots_response = self.sb_read.table('blocked_slots')\
                .select('block_time')\
                .eq('block_date', date)\
                .not_.is_('block_time', None)\
                .execute()
            
            blocked_slots = [item['block_time'] for item in blocked_slots_response.data] if blocked_slots_response.data else []
            
            # Генерируем доступные слоты: последняя сессия начинается не позже (work_end - session_duration)
            slots = []
            try:
                base_date = datetime.strptime(date, "%Y-%m-%d").date()
            except Exception:
                base_date = now_msk().date()
            current_time = datetime.combine(base_date, work_start)
            end_time = datetime.combine(base_date, work_end)
            last_start_time = end_time - timedelta(minutes=session_duration)
            
            while current_time <= last_start_time:
                time_slot = current_time.strftime('%H:%M')
                
                time_available, _ = self.is_time_available(date, time_slot)
                
                if (time_slot not in booked_slots and 
                    time_slot not in blocked_slots and 
                    time_available):
                    slots.append(time_slot)
                
                current_time += timedelta(minutes=session_duration)
            
            return slots
        except Exception as e:
            print(f"❌ Ошибка получения доступных слотов: {e}")
            return []
    
    def is_time_available(self, selected_date: str, time_slot: str) -> Tuple[bool, str]:
        """Проверка доступности времени"""
        try:
            booking_datetime = combine_msk(selected_date, time_slot)
            time_diff = (booking_datetime - now_msk()).total_seconds()
            
            min_advance = BOOKING_RULES["MIN_ADVANCE_HOURS"] * 3600
            
            if time_diff < 0:
                return False, "❌ Это время уже прошло"
            elif time_diff < min_advance:
                return False, f"❌ Запись возможна не менее чем за {BOOKING_RULES['MIN_ADVANCE_HOURS']} час до начала"
            else:
                return True, "✅ Время доступно"
        except ValueError:
            return False, "❌ Неверный формат времени"
    
    def _calculate_time_until(self, date_str: str, time_str: str) -> timedelta:
        """Вычисление времени до события"""
        try:
            event_datetime = combine_msk(date_str, time_str)
            return event_datetime - now_msk()
        except:
            return timedelta(0)
    
    def update_booking_status(self, booking_id: int, new_status: str) -> Tuple[bool, str]:
        """Обновление статуса записи"""
        try:
            self.sb_write.table('bookings').update({'status': new_status}).eq('id', booking_id).execute()
            # При изменении статуса уведомляем при отмене или подтверждении
            try:
                from services.notification_service import NotificationService
                ns = NotificationService()
                resp = self.sb_read.table('bookings').select('*').eq('id', booking_id).limit(1).execute()
                row = resp.data[0] if resp.data else None
                if row:
                    chat_id = row.get('telegram_chat_id') or ns.get_client_telegram_chat_id(row.get('client_phone',''))
                    if str(new_status) == 'cancelled':
                        try:
                            ns.notify_booking_cancelled(row, chat_id)
                        except Exception:
                            pass
                    elif str(new_status) == 'confirmed':
                        try:
                            ns.notify_booking_paid(row, chat_id)
                        except Exception:
                            pass
            except Exception:
                pass
            return True, f"✅ Статус изменен на {new_status}"
        except Exception as e:
            return False, f"❌ Ошибка: {str(e)}"

    def has_paid_first_consultation(self, phone: str) -> bool:
        """True если у клиента уже есть оплаченная первая консультация."""
        try:
            phone_hash = hash_password(normalize_phone(phone))
            return self.has_paid_first_consultation_by_phone_hash(phone_hash)
        except Exception:
            return False

    def has_paid_first_consultation_by_phone_hash(self, phone_hash: str) -> bool:
        """Проверка по phone_hash наличия оплаченной первой консультации (confirmed/completed)."""
        try:
            resp = self.sb_read.table('bookings')\
                .select('product_id')\
                .eq('phone_hash', phone_hash)\
                .in_('status', ['confirmed', 'completed'])\
                .not_.is_('product_id', None)\
                .limit(1000)\
                .execute()
            rows = resp.data or []
            prod_ids = list({r.get('product_id') for r in rows if r.get('product_id') is not None})
            if not prod_ids:
                return False
            prods_resp = self.sb_read.table('products')\
                .select('id, sku, name')\
                .in_('id', prod_ids)\
                .limit(1000)\
                .execute()
            for p in (prods_resp.data or []):
                sku_val = (p.get('sku') or '').upper()
                name_val = (p.get('name') or '').lower()
                if sku_val == 'FIRST_SESSION' or ('перва' in name_val and 'консультац' in name_val):
                    return True
            return False
        except Exception as e:
            print(f"❌ Ошибка проверки первой консультации: {e}")
            return False

    def update_booking_details(self, booking_id: int, new_date: Optional[str] = None, new_time: Optional[str] = None, new_notes: Optional[str] = None) -> Tuple[bool, str]:
        """Обновление даты, времени и комментария записи (частично)."""
        try:
            payload: Dict[str, Any] = {}
            if new_date is not None:
                payload['booking_date'] = new_date
            if new_time is not None:
                payload['booking_time'] = new_time
            if new_notes is not None:
                payload['notes'] = new_notes
            if not payload:
                return True, "Нет изменений"
            self.sb_write.table('bookings').update(payload).eq('id', booking_id).execute()
            return True, "✅ Данные обновлены"
        except Exception as e:
            return False, f"❌ Ошибка обновления: {e}"