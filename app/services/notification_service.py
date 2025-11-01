import requests
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from config.settings import config
from utils.formatters import format_date
from utils.datetime_helpers import now_msk, combine_msk

class TelegramBotService:
    def __init__(self):
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.admin_chat_id = config.TELEGRAM_ADMIN_CHAT_ID
        self.bot_username = config.TELEGRAM_BOT_USERNAME
        self.enabled = config.TELEGRAM_ENABLED
    
    def _send_message(self, chat_id: str, message: str, parse_mode: str = 'HTML') -> bool:
        """Базовая отправка сообщения в Telegram"""
        try:
            if not self.enabled or not self.bot_token:
                return False
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Ошибка Telegram ({response.status_code}): {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка отправки в Telegram: {e}")
            return False
    
    def send_to_admin(self, message: str) -> bool:
        """Отправка сообщения администратору"""
        return self._send_message(self.admin_chat_id, message)
    
    def send_to_client(self, client_chat_id: str, message: str) -> bool:
        """Отправка сообщения клиенту"""
        return self._send_message(client_chat_id, message)
    
    def check_client_connection(self, chat_id: str) -> bool:
        """Проверка подключения клиента к боту"""
        try:
            test_message = "🔍 Проверка подключения..."
            return self._send_message(chat_id, test_message)
        except:
            return False
    
    def get_bot_link(self, client_phone: str = None) -> str:
        """Получение ссылки на бота с параметрами"""
        base_url = f"https://t.me/{self.bot_username}"
        if client_phone:
            from utils.validators import hash_password
            return f"{base_url}?start=connect_{hash_password(client_phone)[:10]}"
        return base_url
    
    def notify_booking_created_admin(self, booking_data: Dict[str, Any]) -> bool:
        """Уведомление админу о новой записи"""
        name = booking_data.get('client_name', 'Клиент')
        phone = booking_data.get('client_phone', 'Не указан')
        date = format_date(booking_data.get('booking_date', ''))
        time = booking_data.get('booking_time', '')
        
        message = f"""
📅 <b>НОВАЯ ЗАПИСЬ НА КОНСУЛЬТАЦИЮ</b>

👤 <b>Клиент:</b> {name}
📱 <b>Телефон:</b> <code>{phone}</code>
📅 <b>Дата:</b> {date}
🕐 <b>Время:</b> {time}

⏰ <i>Напоминание будет отправлено за 1 час до консультации</i>
        """
        
        return self.send_to_admin(message)
    
    def notify_booking_created_client(self, client_chat_id: str, booking_data: Dict[str, Any]) -> bool:
        """Уведомление клиенту о подтверждении записи"""
        name = booking_data.get('client_name', '')
        date = format_date(booking_data.get('booking_date', ''))
        time = booking_data.get('booking_time', '')
        
        message = f"""
✅ <b>ВАША ЗАПИСЬ ПОДТВЕРЖДЕНА</b>

Добрый день, {name}!

📅 <b>Дата:</b> {date}
🕐 <b>Время:</b> {time}

Мы ждем вас на консультацию!

⏰ <i>Мы напомним вам за 1 час до начала</i>

Если у вас возникли вопросы, ответьте на это сообщение.
        """
        
        return self.send_to_client(client_chat_id, message)

    def notify_booking_paid_admin(self, booking_data: Dict[str, Any]) -> bool:
        """Уведомление админу об оплате записи"""
        name = booking_data.get('client_name', 'Клиент')
        phone = booking_data.get('client_phone', 'Не указан')
        date = format_date(booking_data.get('booking_date', ''))
        time = booking_data.get('booking_time', '')

        message = f"""
💳 <b>ОПЛАТА ЗА КОНСУЛЬТАЦИЮ</b>

👤 <b>Клиент:</b> {name}
📱 <b>Телефон:</b> <code>{phone}</code>
📅 <b>Дата:</b> {date}
🕐 <b>Время:</b> {time}

📌 Статус: <b>Оплачено</b>
        """

        return self.send_to_admin(message)

    def notify_booking_paid_client(self, client_chat_id: str, booking_data: Dict[str, Any]) -> bool:
        """Уведомление клиенту об успешной оплате"""
        name = booking_data.get('client_name', '')
        date = format_date(booking_data.get('booking_date', ''))
        time = booking_data.get('booking_time', '')

        message = f"""
✅ <b>ПОДТВЕРЖДЕНИЕ ОПЛАТЫ</b>

Добрый день, {name}!

Спасибо за оплату. Ваша запись подтверждена.

📅 <b>Дата:</b> {date}
🕐 <b>Время:</b> {time}

Мы отправим напоминание за 1 час до встречи.
        """

        return self.send_to_client(client_chat_id, message)
    
    def notify_booking_cancelled_admin(self, booking_data: Dict[str, Any]) -> bool:
        """Уведомление админу об отмене записи"""
        name = booking_data.get('client_name', 'Клиент')
        phone = booking_data.get('client_phone', 'Не указан')
        date = format_date(booking_data.get('booking_date', ''))
        time = booking_data.get('booking_time', '')

        message = f"""
❌ <b>ЗАПИСЬ ОТМЕНЕНА</b>

👤 <b>Клиент:</b> {name}
📱 <b>Телефон:</b> <code>{phone}</code>
📅 <b>Дата:</b> {date}
🕐 <b>Время:</b> {time}
        """
        return self.send_to_admin(message)

    def notify_booking_cancelled_client(self, client_chat_id: str, booking_data: Dict[str, Any]) -> bool:
        """Уведомление клиенту об отмене записи"""
        date = format_date(booking_data.get('booking_date', ''))
        time = booking_data.get('booking_time', '')

        message = f"""
❌ <b>ВАША ЗАПИСЬ ОТМЕНЕНА</b>

📅 <b>Дата:</b> {date}
🕐 <b>Время:</b> {time}

Если это произошло по ошибке, пожалуйста, запишитесь снова.
        """
        return self.send_to_client(client_chat_id, message)
    
    def schedule_reminder(self, booking_data: Dict[str, Any], client_chat_id: str):
        """Планирование напоминания за 1 час до консультации"""
        try:
            booking_date = booking_data.get('booking_date')
            booking_time = booking_data.get('booking_time')
            
            if not booking_date or not booking_time:
                return
            
            # Создаем datetime объекта консультации
            consultation_datetime = combine_msk(booking_date, booking_time)
            
            # Вычисляем время напоминания (за 1 час)
            reminder_time = consultation_datetime - timedelta(hours=1)
            
            # Вычисляем задержку в секундах
            now = now_msk()
            delay_seconds = (reminder_time - now).total_seconds()
            
            # Если напоминание должно быть в будущем
            if delay_seconds > 0:
                # Запускаем в отдельном потоке
                timer = threading.Timer(
                    delay_seconds, 
                    self._send_reminder, 
                    [booking_data, client_chat_id]
                )
                timer.daemon = True
                timer.start()
                
                print(f"⏰ Напоминание запланировано на {reminder_time}")
            else:
                print("⚠️ Время консультации уже прошло, напоминание не планируется")
                
        except Exception as e:
            print(f"❌ Ошибка планирования напоминания: {e}")
    
    def _send_reminder(self, booking_data: Dict[str, Any], client_chat_id: str):
        """Отправка запланированного напоминания"""
        try:
            print("🔔 Отправка запланированного напоминания...")
            
            # Отправляем напоминания
            self.notify_reminder_admin(booking_data)
            self.notify_reminder_client(client_chat_id, booking_data)
            
            print("✅ Напоминания отправлены!")
                
        except Exception as e:
            print(f"❌ Ошибка отправки напоминания: {e}")
    
    def notify_reminder_admin(self, booking_data: Dict[str, Any]) -> bool:
        """Напоминание админу за 1 час"""
        name = booking_data.get('client_name', 'Клиент')
        phone = booking_data.get('client_phone', 'Не указан')
        time = booking_data.get('booking_time', '')
        
        message = f"""
⏰ <b>НАПОМИНАНИЕ О КОНСУЛЬТАЦИИ</b>

Через 1 час у вас консультация:

👤 <b>Клиент:</b> {name}
📱 <b>Телефон:</b> <code>{phone}</code>
🕐 <b>Время:</b> {time}

Подготовьтесь к встрече!
        """
        
        return self.send_to_admin(message)
    
    def notify_reminder_client(self, client_chat_id: str, booking_data: Dict[str, Any]) -> bool:
        """Напоминание клиенту за 1 час"""
        name = booking_data.get('client_name', '')
        time = booking_data.get('booking_time', '')
        
        message = f"""
⏰ <b>НАПОМИНАНИЕ О КОНСУЛЬТАЦИИ</b>

Добрый день, {name}!

Через 1 час у вас консультация в {time}.

Пожалуйста, подготовьтесь к встрече.

Ждем вас!
        """
        
        return self.send_to_client(client_chat_id, message)

class NotificationService:
    def __init__(self):
        self.bot = TelegramBotService()
        from core.database import db_manager
        self.supabase = db_manager.get_client()
    
    def notify_booking_created(self, booking_data: Dict[str, Any], client_chat_id: str = None) -> Dict[str, bool]:
        """Полный цикл уведомлений о новой записи"""
        results = {}
        
        # Уведомление администратору
        results['admin_notified'] = self.bot.notify_booking_created_admin(booking_data)
        
        # Уведомление клиенту (если указан chat_id)
        if client_chat_id:
            results['client_notified'] = self.bot.notify_booking_created_client(client_chat_id, booking_data)
            
            # Планируем напоминание за 1 час ТОЛЬКО для подтвержденных записей
            try:
                if str(booking_data.get('status')) == 'confirmed':
                    self.bot.schedule_reminder(booking_data, client_chat_id)
                    results['reminder_scheduled'] = True
                else:
                    results['reminder_scheduled'] = False
            except Exception:
                results['reminder_scheduled'] = False
        
        return results

    def notify_booking_paid(self, booking_data: Dict[str, Any], client_chat_id: str = None) -> Dict[str, bool]:
        """Уведомления при оплате: админу + клиенту (если подключён), и планирование напоминания."""
        results = {}
        try:
            results['admin_notified'] = self.bot.notify_booking_paid_admin(booking_data)
        except Exception:
            results['admin_notified'] = False

        if client_chat_id:
            try:
                results['client_notified'] = self.bot.notify_booking_paid_client(client_chat_id, booking_data)
            except Exception:
                results['client_notified'] = False

            # Планируем напоминание за 1 час
            try:
                self.bot.schedule_reminder(booking_data, client_chat_id)
                results['reminder_scheduled'] = True
            except Exception:
                results['reminder_scheduled'] = False
        else:
            results['client_notified'] = False
            results['reminder_scheduled'] = False

        return results

    def notify_booking_cancelled(self, booking_data: Dict[str, Any], client_chat_id: str = None) -> Dict[str, bool]:
        """Уведомления при отмене: админу + клиенту (если подключён)."""
        results = {}
        try:
            results['admin_notified'] = self.bot.notify_booking_cancelled_admin(booking_data)
        except Exception:
            results['admin_notified'] = False

        if client_chat_id:
            try:
                results['client_notified'] = self.bot.notify_booking_cancelled_client(client_chat_id, booking_data)
            except Exception:
                results['client_notified'] = False
        else:
            results['client_notified'] = False

        return results
    
    def save_telegram_chat_id(self, phone: str, chat_id: str) -> bool:
        """Сохранение Telegram chat_id клиента"""
        try:
            from utils.validators import hash_password, normalize_phone
            phone_hash = hash_password(normalize_phone(phone))
            
            # Обновляем все записи клиента
            response = self.supabase.table('bookings')\
                .update({'telegram_chat_id': chat_id})\
                .eq('phone_hash', phone_hash)\
                .execute()
            
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения chat_id: {e}")
            return False
    
    def get_client_telegram_chat_id(self, phone: str) -> Optional[str]:
        """Получение Telegram chat_id клиента"""
        try:
            from utils.validators import hash_password, normalize_phone
            phone_hash = hash_password(normalize_phone(phone))
            
            response = self.supabase.table('bookings')\
                .select('telegram_chat_id')\
                .eq('phone_hash', phone_hash)\
                .not_.is_('telegram_chat_id', None)\
                .limit(1)\
                .execute()
            
            if response.data and response.data[0]['telegram_chat_id']:
                return response.data[0]['telegram_chat_id']
            return None
        except Exception as e:
            print(f"❌ Ошибка получения chat_id: {e}")
            return None