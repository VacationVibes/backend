import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal

from pydantic import BaseModel, EmailStr, constr

from src.auth.schemas import UserScheme
from src.models import PlaceModel


class ReactionData(BaseModel):
    place_id: uuid.UUID
    reaction: Literal['like', 'dislike']


class SuccessResponse(BaseModel):
    success: bool
    message: str


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


class ReactionsList(BaseModel):
    success: bool
    reactions: list[PlaceReactionScheme]
