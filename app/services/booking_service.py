import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from models.booking import Booking
from core.database import db_manager
from config.constants import BOOKING_RULES
from utils.validators import normalize_phone, hash_password
from utils.datetime_helpers import now_msk, combine_msk

class BookingService:
    
    def __init__(self):
        self.sb_read = db_manager.get_client()
        self.sb_write = db_manager.get_service_client() or self.sb_read
    
    # ========== КЭШИРОВАННЫЕ МЕТОДЫ ==========
    
    @st.cache_data(ttl=60, show_spinner=False)
    def get_available_slots(_self, date: str) -> List[str]:
        """КЭШИРОВАННАЯ версия получения доступных слотов (TTL 60 сек)"""
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
            blocked_response = _self.sb_read.table('blocked_slots')\
                .select('id')\
                .eq('block_date', date)\
                .is_('block_time', None)\
                .execute()
            
            if blocked_response.data:
                return []
            
            # Занятые слоты
            booked_response = _self.sb_read.table('bookings')\
                .select('booking_time')\
                .eq('booking_date', date)\
                .neq('status', 'cancelled')\
                .execute()
            
            booked_slots = [item['booking_time'] for item in booked_response.data] if booked_response.data else []
            
            # Заблокированные слоты
            blocked_slots_response = _self.sb_read.table('blocked_slots')\
                .select('block_time')\
                .eq('block_date', date)\
                .not_.is_('block_time', None)\
                .execute()
            
            blocked_slots = [item['block_time'] for item in blocked_slots_response.data] if blocked_slots_response.data else []
            
            # Генерация слотов
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
                
                if (time_slot not in booked_slots and 
                    time_slot not in blocked_slots):
                    # Упрощённая проверка доступности времени
                    booking_datetime = combine_msk(date, time_slot)
                    time_diff = (booking_datetime - now_msk()).total_seconds()
                    min_advance = BOOKING_RULES["MIN_ADVANCE_HOURS"] * 3600
                    
                    if time_diff >= min_advance:
                        slots.append(time_slot)
                
                current_time += timedelta(minutes=session_duration)
            
            return slots
        except Exception as e:
            print(f"❌ Ошибка получения доступных слотов: {e}")
            return []
    
    @st.cache_data(ttl=30, show_spinner=False)
    def get_upcoming_client_booking(_self, phone: str) -> Optional[Dict[str, Any]]:
        """КЭШИРОВАННАЯ версия получения ближайшей записи (TTL 30 сек)"""
        try:
            phone_hash = hash_password(normalize_phone(phone))
            response = _self.sb_read.table('bookings')\
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
    
    @st.cache_data(ttl=30, show_spinner=False)
    def get_latest_pending_booking_for_client(_self, phone: str) -> Optional[Dict[str, Any]]:
        """КЭШИРОВАННАЯ версия получения неоплаченного заказа (TTL 30 сек)"""
        try:
            phone_hash = hash_password(normalize_phone(phone))
            response = _self.sb_read.table('bookings')\
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
    
    # ========== МЕТОДЫ БЕЗ ИЗМЕНЕНИЙ (но с инвалидацией кэша) ==========
    
    def create_booking(self, booking_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Создание записи с инвалидацией кэша"""
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
                # Инвалидация кэша
                st.cache_data.clear()
                return True, "✅ Запись успешно создана"
            return False, "❌ Ошибка при создании записи"
            
        except Exception as e:
            if "duplicate key" in str(e) or "unique constraint" in str(e):
                return False, "❌ Это время уже занято"
            return False, f"❌ Ошибка: {str(e)}"
    
    def cancel_booking(self, booking_id: int, phone: str) -> Tuple[bool, str]:
        """Отмена записи с инвалидацией кэша"""
        try:
            phone_hash = hash_password(normalize_phone(phone))
            
            response = self.sb_read.table('bookings')\
                .select('*')\
                .eq('id', booking_id)\
                .eq('phone_hash', phone_hash)\
                .execute()
            
            if not response.data:
                return False, "Запись не найдена"
            
            booking = response.data[0]
            
            time_until = self._calculate_time_until(booking['booking_date'], booking['booking_time'])
            min_cancel = BOOKING_RULES["MIN_CANCEL_MINUTES"] * 60
            
            if time_until.total_seconds() < min_cancel:
                return False, f"Отмена возможна не позднее чем за {BOOKING_RULES['MIN_CANCEL_MINUTES']} минут"
            
            self.sb_write.table('bookings')\
                .update({'status': 'cancelled'})\
                .eq('id', booking_id)\
                .execute()
            
            # Инвалидация кэша
            st.cache_data.clear()
            
            return True, "Запись успешно отменена"
            
        except Exception as e:
            return False, f"❌ Ошибка: {str(e)}"
    
    def mark_booking_paid(self, booking_id: int) -> Tuple[bool, str]:
        """Отметка оплаты с инвалидацией кэша"""
        try:
            payload: Dict[str, Any] = {'status': 'confirmed'}
            try:
                payload['paid_at'] = now_msk().isoformat()
            except Exception:
                pass
            self.sb_write.table('bookings').update(payload).eq('id', booking_id).execute()
            
            # Инвалидация кэша
            st.cache_data.clear()
            
            return True, "✅ Отмечено как оплачено"
        except Exception as e:
            return False, f"❌ Ошибка отметки оплаты: {e}"
    
    # ========== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ==========
    
    def _calculate_time_until(self, date_str: str, time_str: str) -> timedelta:
        """Вычисление времени до события"""
        try:
            event_datetime = combine_msk(date_str, time_str)
            return event_datetime - now_msk()
        except:
            return timedelta(0)
    
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
    
    # ========== МЕТОДЫ БЕЗ КЭША (используются редко) ==========
    
    def get_all_bookings(self, date_from: str = None, date_to: str = None) -> pd.DataFrame:
        """Получение всех записей (БЕЗ кэша для админки)"""
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
        """Получение записей клиента (БЕЗ кэша)"""
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
    
    def has_active_booking(self, phone: str) -> bool:
        """Проверка активной записи"""
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
    
    def delete_booking(self, booking_id: int) -> bool:
        """Удаление записи с инвалидацией кэша"""
        try:
            self.sb_write.table('bookings').delete().eq('id', booking_id).execute()
            st.cache_data.clear()
            return True
        except Exception as e:
            print(f"❌ Ошибка удаления записи: {e}")
            return False
    
    def get_booking_by_datetime(self, phone: str, date_str: str, time_str: str) -> Optional[Dict[str, Any]]:
        """Получить запись по дате/времени"""
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
            print(f"❌ Ошибка поиска записи: {e}")
            return None
    
    def set_booking_payment_info(self, booking_id: int, product_id: Optional[int], amount: Optional[float]) -> bool:
        """Сохранить продукт и сумму"""
        try:
            payload: Dict[str, Any] = {}
            if product_id is not None:
                payload['product_id'] = product_id
            if amount is not None:
                payload['amount'] = amount
            if not payload:
                return True
            self.sb_write.table('bookings').update(payload).eq('id', booking_id).execute()
            st.cache_data.clear()
            return True
        except Exception as e:
            print(f"⚠️ Не удалось сохранить продукт/сумму: {e}")
            return False
    
    def update_booking_status(self, booking_id: int, new_status: str) -> Tuple[bool, str]:
        """Обновление статуса"""
        try:
            self.sb_write.table('bookings').update({'status': new_status}).eq('id', booking_id).execute()
            st.cache_data.clear()
            return True, f"✅ Статус изменен на {new_status}"
        except Exception as e:
            return False, f"❌ Ошибка: {str(e)}"
    
    def has_paid_first_consultation(self, phone: str) -> bool:
        """Проверка оплаченной первой консультации"""
        try:
            phone_hash = hash_password(normalize_phone(phone))
            return self.has_paid_first_consultation_by_phone_hash(phone_hash)
        except Exception:
            return False
    
    def has_paid_first_consultation_by_phone_hash(self, phone_hash: str) -> bool:
        """Проверка по phone_hash"""
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
    
    def update_booking_details(self, booking_id: int, new_date: Optional[str] = None, 
                              new_time: Optional[str] = None, new_notes: Optional[str] = None) -> Tuple[bool, str]:
        """Обновление деталей записи"""
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
            st.cache_data.clear()
            return True, "✅ Данные обновлены"
        except Exception as e:
            return False, f"❌ Ошибка обновления: {e}"
    
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
                st.cache_data.clear()
                return True, "✅ Запись успешно создана"
            return False, "❌ Ошибка при создании записи"
                
        except Exception as e:
            if "duplicate key" in str(e) or "unique constraint" in str(e):
                return False, "❌ Это время уже занято"
            return False, f"❌ Ошибка: {str(e)}"