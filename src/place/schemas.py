import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel


class ReactionData(BaseModel):
    place_id: uuid.UUID
    reaction: Literal['like', 'dislike']


class SuccessResponse(BaseModel):
    success: bool
    message: str


class PlaceTypeMin(BaseModel):
    type: str


class PlaceImageMin(BaseModel):
    image_url: str


class PlaceReactionMin(BaseModel):
    reaction: Literal['like', 'dislike']
    created_at: datetime


class PlaceMin(BaseModel):
    id: uuid.UUID
    name: str
    # place_id: str
    latitude: Decimal
    longitude: Decimal
    created_at: datetime
    types: list[PlaceTypeMin]
    images: list[PlaceImageMin]
    reactions: Optional[list[PlaceReactionMin]] = []  # not always loaded


class ReactionsList(BaseModel):
    success: bool
    reactions: list[PlaceMin]
