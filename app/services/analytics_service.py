import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple
from core.database import db_manager
from utils.formatters import get_month_end
from utils.datetime_helpers import now_msk

class AnalyticsService:
    def __init__(self):
        self.supabase = db_manager.get_client()
    
    def get_stats(self) -> Tuple[int, int, int, int]:
        """Получение основной статистики"""
        try:
            # Общее количество записей
            total_response = self.supabase.table('bookings').select('id', count='exact').execute()
            total = total_response.count or 0
            
            # Предстоящие записи
            upcoming_response = self.supabase.table('bookings')\
                .select('id', count='exact')\
                .eq('status', 'confirmed')\
                .gte('booking_date', now_msk().date().isoformat())\
                .execute()
            upcoming = upcoming_response.count or 0
            
            # Записи за текущий месяц
            current_date = now_msk()
            month_start = current_date.replace(day=1).date().isoformat()
            month_end = get_month_end(current_date.year, current_date.month)
            
            monthly_response = self.supabase.table('bookings')\
                .select('id', count='exact')\
                .gte('booking_date', month_start)\
                .lte('booking_date', month_end)\
                .execute()
            this_month = monthly_response.count or 0
            
            # Записи за последние 7 дней
            week_ago = (now_msk() - timedelta(days=7)).date().isoformat()
            weekly_response = self.supabase.table('bookings')\
                .select('id', count='exact')\
                .gte('booking_date', week_ago)\
                .execute()
            this_week = weekly_response.count or 0
            
            return total, upcoming, this_month, this_week
        except Exception as e:
            print(f"❌ Ошибка получения статистики: {e}")
            return 0, 0, 0, 0

    def get_product_summary(self, date_from: str = None, date_to: str = None, statuses: list | None = None) -> pd.DataFrame:
        """Агрегация по продуктам: количество заказов и сумма.
        Фильтры: даты (по booking_date) и статусы.
        """
        try:
            if self.supabase is None:
                return pd.DataFrame()
            bq = self.supabase.table('bookings').select('product_id, amount, status, booking_date')
            if date_from:
                bq = bq.gte('booking_date', date_from)
            if date_to:
                bq = bq.lte('booking_date', date_to)
            if statuses:
                bq = bq.in_('status', statuses)
            bresp = bq.execute()
            rows = bresp.data or []
            if not rows:
                return pd.DataFrame(columns=['product_id','product_name','count','revenue'])
            df = pd.DataFrame(rows)
            # Берем только строки с product_id
            df = df[df['product_id'].notna()]
            if df.empty:
                return pd.DataFrame(columns=['product_id','product_name','count','revenue'])
            # Загружаем продукты
            prods = self.supabase.table('products').select('id, name').execute().data or []
            prod_map = {p['id']: p.get('name') for p in prods if p.get('id') is not None}
            # amount может быть None — трактуем как 0
            if 'amount' not in df.columns:
                df['amount'] = 0.0
            df['amount'] = df['amount'].fillna(0.0).astype(float)
            grouped = df.groupby('product_id').agg(count=('product_id','size'), revenue=('amount','sum')).reset_index()
            grouped['product_name'] = grouped['product_id'].apply(lambda x: prod_map.get(x, f"ID {x}"))
            grouped = grouped[['product_id','product_name','count','revenue']]
            return grouped
        except Exception as e:
            print(f"❌ Ошибка получения сводки по продуктам: {e}")
            return pd.DataFrame(columns=['product_id','product_name','count','revenue'])