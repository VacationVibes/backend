from decimal import Decimal
from typing import Literal
from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr


class UserScheme(BaseModel):
    id: uuid.UUID
    email: EmailStr

    class Config:
        from_attributes = True


class UserSchemeDetailed(BaseModel):
    id: uuid.UUID
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class PlaceScheme(BaseModel):
    id: uuid.UUID
    place_id: str
    latitude: Decimal
    longitude: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class PlaceReactionScheme(BaseModel):
    id: uuid.UUID
    place: PlaceScheme
    # user: UserScheme
    reaction: Literal['like', 'dislike']
    created_at: datetime

    class Config:
        from_attributes = True
