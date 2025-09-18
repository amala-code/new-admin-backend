
from typing import Optional
from pydantic import BaseModel, EmailStr
from dataclasses import dataclass, field
from datetime import datetime

class Member(BaseModel):
    name: str
    address: str
    email: EmailStr
    phone: str
    id: str  # Custom ID field
    year_of_joining: int = field(default_factory=lambda: datetime.now().year)
    amount_paid_total: float=0
    member_true: bool = False  # Default to False
    amount_paid_registration: float=0
    amount_paid_subscription: float=0
    amount_subscription: bool=False
    date_of_subscription: Optional[str] = None
    transaction_id: Optional[str] = None
    

class MemberUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    year_of_joining: Optional[int] = None
    amount_paid_total: Optional[float] = None
    member_true: Optional[bool] = None
    amount_paid_registration: Optional[float] = None
    amount_paid_subscription: Optional[float] = None
    amount_subscription: Optional[bool] = False
    date_of_subscription: Optional[str] = None
    transaction_id: Optional[str] = None

class NonMember(BaseModel):
    name: str
    phone: str
    email: EmailStr
    note: Optional[str] = None
    id: Optional[str] = None