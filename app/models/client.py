from dataclasses import dataclass
from typing import Optional

@dataclass
class Client:
    phone_hash: str
    client_name: str
    client_phone: str
    client_email: Optional[str] = None
    client_telegram: Optional[str] = None
    total_bookings: int = 0
    upcoming_bookings: int = 0
    completed_bookings: int = 0
    cancelled_bookings: int = 0
    first_booking: Optional[str] = None
    last_booking: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Client':
        return cls(
            phone_hash=data.get('phone_hash', ''),
            client_name=data.get('client_name', ''),
            client_phone=data.get('client_phone', ''),
            client_email=data.get('client_email'),
            client_telegram=data.get('client_telegram'),
            total_bookings=data.get('total_bookings', 0),
            upcoming_bookings=data.get('upcoming_bookings', 0),
            completed_bookings=data.get('completed_bookings', 0),
            cancelled_bookings=data.get('cancelled_bookings', 0),
            first_booking=data.get('first_booking'),
            last_booking=data.get('last_booking')
        )