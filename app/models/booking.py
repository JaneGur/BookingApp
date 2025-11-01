from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Booking:
    id: Optional[int] = None
    client_name: str = ""
    client_phone: str = ""
    client_email: Optional[str] = None
    client_telegram: Optional[str] = None
    booking_date: str = ""
    booking_time: str = ""
    notes: Optional[str] = None
    status: str = "confirmed"
    phone_hash: str = ""
    telegram_chat_id: Optional[str] = None
    created_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Booking':
        return cls(
            id=data.get('id'),
            client_name=data.get('client_name', ''),
            client_phone=data.get('client_phone', ''),
            client_email=data.get('client_email'),
            client_telegram=data.get('client_telegram'),
            booking_date=data.get('booking_date', ''),
            booking_time=data.get('booking_time', ''),
            notes=data.get('notes'),
            status=data.get('status', 'confirmed'),
            phone_hash=data.get('phone_hash', ''),
            telegram_chat_id=data.get('telegram_chat_id'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self) -> dict:
        return {
            'client_name': self.client_name,
            'client_phone': self.client_phone,
            'client_email': self.client_email,
            'client_telegram': self.client_telegram,
            'booking_date': self.booking_date,
            'booking_time': self.booking_time,
            'notes': self.notes,
            'status': self.status,
            'phone_hash': self.phone_hash,
            'telegram_chat_id': self.telegram_chat_id
        }