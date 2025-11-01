# Система записи (Streamlit + Supabase)

## Запуск
1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Создайте файл переменных окружения (локально, не коммитьте в git):
   ```env
   SUPABASE_URL=...
   SUPABASE_KEY=...
   TELEGRAM_BOT_TOKEN=...
   TELEGRAM_ADMIN_CHAT_ID=...
   TELEGRAM_BOT_USERNAME=Jenyhelperbot
   TELEGRAM_ENABLED=true
   # Один из вариантов ниже (bcrypt предпочтительнее)
   ADMIN_PASSWORD_BCRYPT=$2b$12$...
   # или (legacy sha256)
   ADMIN_PASSWORD_HASH=...
   ```
3. Запустите приложение:
   ```bash
   streamlit run app/main.py
   ```

## Миграции схемы (Supabase)
Выполните SQL (однократно):
```sql
CREATE TABLE IF NOT EXISTS client_auth (
  phone_hash TEXT PRIMARY KEY,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Индексы/ограничения для таблицы записей
CREATE UNIQUE INDEX IF NOT EXISTS bookings_unique_slot
  ON bookings(booking_date, booking_time)
  WHERE status <> 'cancelled';
CREATE INDEX IF NOT EXISTS bookings_phone_idx ON bookings(phone_hash);
```

## Безопасность
- Не храните .env в репозитории. Секреты — только в ENV/Streamlit secrets/CI secrets.
- Пароли клиентов хэшируются через bcrypt (legacy sha256 поддерживается для совместимости).
- Хэш админ-пароля передавайте через `ADMIN_PASSWORD_BCRYPT` или `ADMIN_PASSWORD_HASH`.

## Разработка
- Линтинг и типизация:
  ```bash
  ruff check app
  mypy app
  pytest
  ```
