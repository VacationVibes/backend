import uuid
from typing import Literal

from pydantic import BaseModel

from src.schemas import PlaceReactionScheme


class ReactionData(BaseModel):
    place_id: uuid.UUID
    reaction: Literal['like', 'dislike']


class SuccessResponse(BaseModel):
    success: bool
    message: str


class ReactionsList(BaseModel):
    success: bool
    reactions: list[PlaceReactionScheme]
