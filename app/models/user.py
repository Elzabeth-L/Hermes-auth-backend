from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class UserInDB(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
    password_hash: str
    role: Literal["customer"] = "customer"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
