from decimal import Decimal
from typing import Literal, Optional
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


class PlaceTypeScheme(BaseModel):
    place_id: uuid.UUID
    type: str
    created_at: datetime

    class Config:
        from_attributes = True


class PlaceImageScheme(BaseModel):
    place_id: uuid.UUID
    image_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class PlaceReactionScheme(BaseModel):
    id: uuid.UUID
    reaction: Literal['like', 'dislike']
    created_at: datetime

    class Config:
        from_attributes = True


class PlaceScheme(BaseModel):
    id: uuid.UUID
    name: str
    place_id: str
    latitude: Decimal
    longitude: Decimal
    created_at: datetime
    types: list[PlaceTypeScheme] = []
    images: list[PlaceImageScheme] = []
    reactions: Optional[list[PlaceReactionScheme]] = []  # not always loaded

    class Config:
        from_attributes = True
