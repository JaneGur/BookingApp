import pandas as pd
from typing import Optional, Dict, Any, List
from models.client import Client
from core.database import db_manager
from utils.validators import normalize_phone, hash_password, format_phone
from typing import Tuple

class ClientService:
    def __init__(self):
        self.supabase = db_manager.get_client()
    
    # === Профиль клиента (client_profiles) ===
    def get_profile(self, phone: str) -> Optional[Dict[str, Any]]:
        """Получить профиль клиента из client_profiles. Возвращает None, если нет таблицы или записи"""
        try:
            phone_norm = normalize_phone(phone)
            phone_hash = hash_password(phone_norm)
            resp = self.supabase.table('client_profiles') \
                .select('client_name, client_email, client_telegram, client_phone, phone_hash') \
                .eq('phone_hash', phone_hash) \
                .limit(1) \
                .execute()
            if resp.data:
                return resp.data[0]
            return None
        except Exception:
            # Таблицы может не быть — мягкий фоллбек
            return None

    def upsert_profile(self, phone: str, name: str, email: str, telegram: str) -> bool:
        """Создать/обновить профиль клиента. Мягко обрабатывает отсутствие таблицы"""
        try:
            phone_norm = normalize_phone(phone)
            phone_hash = hash_password(phone_norm)
            payload = {
                'phone_hash': phone_hash,
                'client_phone': phone_norm,
                'client_name': name,
                'client_email': email,
                'client_telegram': telegram,
            }
            # upsert по phone_hash (если поддерживается)
            try:
                self.supabase.table('client_profiles').upsert(payload, on_conflict='phone_hash').execute()
            except Exception:
                # Фоллбек: попытка найти и затем insert/update
                existing = self.supabase.table('client_profiles').select('phone_hash').eq('phone_hash', phone_hash).execute()
                if existing.data:
                    self.supabase.table('client_profiles').update(payload).eq('phone_hash', phone_hash).execute()
                else:
                    self.supabase.table('client_profiles').insert(payload).execute()
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения профиля: {e}")
            return False

    def get_client_info(self, phone: str) -> Optional[Dict[str, Any]]:
        """Получение информации о клиенте"""
        try:
            phone_hash = hash_password(normalize_phone(phone))
            response = self.supabase.table('bookings').select('client_name, client_email, client_telegram')\
                .eq('phone_hash', phone_hash)\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"❌ Ошибка получения информации о клиенте: {e}")
            return None

    def get_profile_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Получить профиль клиента по email из client_profiles"""
        try:
            if not email:
                return None
            resp = self.supabase.table('client_profiles') \
                .select('client_name, client_email, client_telegram, client_phone, phone_hash') \
                .eq('client_email', email) \
                .limit(1) \
                .execute()
            if resp.data:
                return resp.data[0]
            return None
        except Exception:
            return None
    
    def get_all_clients(self) -> pd.DataFrame:
        """Получение списка всех уникальных клиентов"""
        try:
            response = self.supabase.table('bookings')\
                .select('client_name, client_phone, client_email, client_telegram, phone_hash')\
                .execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                clients_df = df.groupby('phone_hash').first().reset_index()
                
                clients_data = []
                for phone_hash in clients_df['phone_hash'].unique():
                    client_row = clients_df[clients_df['phone_hash'] == phone_hash].iloc[0]
                    
                    bookings_response = self.supabase.table('bookings')\
                        .select('id, status, booking_date')\
                        .eq('phone_hash', phone_hash)\
                        .execute()
                    
                    if bookings_response.data:
                        bookings_df = pd.DataFrame(bookings_response.data)
                        total = len(bookings_df)
                        upcoming = len(bookings_df[bookings_df['status'] == 'confirmed']) if 'status' in bookings_df.columns else 0
                        completed = len(bookings_df[bookings_df['status'] == 'completed']) if 'status' in bookings_df.columns else 0
                        cancelled = len(bookings_df[bookings_df['status'] == 'cancelled']) if 'status' in bookings_df.columns else 0
                        first_booking = bookings_df['booking_date'].min() if 'booking_date' in bookings_df.columns else ''
                        last_booking = bookings_df['booking_date'].max() if 'booking_date' in bookings_df.columns else ''
                    else:
                        total = upcoming = completed = cancelled = 0
                        first_booking = last_booking = ''
                    
                    client_data = {
                        'phone_hash': phone_hash,
                        'client_name': client_row['client_name'],
                        'client_phone': format_phone(client_row['client_phone']),
                        'client_email': client_row['client_email'],
                        'client_telegram': client_row['client_telegram'],
                        'total_bookings': total,
                        'upcoming_bookings': upcoming,
                        'completed_bookings': completed,
                        'cancelled_bookings': cancelled,
                        'first_booking': first_booking,
                        'last_booking': last_booking
                    }
                    clients_data.append(client_data)
                
                return pd.DataFrame(clients_data)
            else:
                return pd.DataFrame()
        except Exception as e:
            print(f"❌ Ошибка получения списка клиентов: {e}")
            return pd.DataFrame()
    
    def get_client_booking_history(self, phone_hash: str) -> pd.DataFrame:
        """Получение истории записей конкретного клиента"""
        try:
            response = self.supabase.table('bookings')\
                .select('*')\
                .eq('phone_hash', phone_hash)\
                .order('booking_date', desc=True)\
                .order('booking_time', desc=True)\
                .execute()
            
            return pd.DataFrame(response.data) if response.data else pd.DataFrame()
        except Exception as e:
            print(f"❌ Ошибка получения истории записей: {e}")
            return pd.DataFrame()

    def delete_client_by_hash(self, phone_hash: str, cascade_bookings: bool = False) -> Tuple[bool, str]:
        """Удалить клиента по phone_hash. При cascade_bookings удаляет и все его записи."""
        try:
            # Для удаления используем сервис-клиент, чтобы обойти RLS
            from core.database import db_manager
            sbw = db_manager.get_service_client() or self.supabase
            if sbw is None:
                return False, "Нет подключения к базе (service client)"
            try:
                sbw.table('client_profiles').delete().eq('phone_hash', phone_hash).execute()
            except Exception as e:
                print(f"delete client_profiles error: {e}")
            try:
                sbw.table('client_auth').delete().eq('phone_hash', phone_hash).execute()
            except Exception as e:
                print(f"delete client_auth error: {e}")
            try:
                sbw.table('client_auth_tokens').delete().eq('phone_hash', phone_hash).execute()
            except Exception as e:
                print(f"delete client_auth_tokens error: {e}")
            if cascade_bookings:
                try:
                    sbw.table('bookings').delete().eq('phone_hash', phone_hash).execute()
                except Exception as e:
                    print(f"delete bookings error: {e}")
            return True, "✅ Клиент удалён"
        except Exception as e:
            return False, f"❌ Ошибка удаления: {e}"