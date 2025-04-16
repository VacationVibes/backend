import uuid

import sqlalchemy
from fastapi import APIRouter, Query, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from src.auth.dependencies import CurrentUserDep
from src.place import service
from src.database import DBSessionDep

from src.place.schemas import ReactionData, SuccessResponse, ReactionsList, PlaceMin, PlaceCommentSchema
from src.schemas import PlaceScheme, PlaceComment

router = APIRouter()


@router.post(
    "/reaction",
    response_model=SuccessResponse
)
async def reaction(
        user: CurrentUserDep,
        reaction_data: ReactionData,
        db_session: DBSessionDep
) -> SuccessResponse:
    await service.add_reaction(db_session, reaction_data, user)
    return SuccessResponse(success=True, message="Reaction successfully added!")


@router.get(
    "/reactions",
    response_model=list[PlaceMin]
)
async def reaction(
        user: CurrentUserDep,
        db_session: DBSessionDep,
        offset: int = Query(0, ge=0),
        limit: int = Query(10, le=100)
) -> list[PlaceScheme]:
    reactions = await service.get_user_reactions(db_session, user, offset, limit)
    return reactions


@router.get(
    "/feed",
    response_model=list[PlaceMin]
)
async def feed(
        user: CurrentUserDep,
        db_session: DBSessionDep,
        ignore_ids: list[uuid.UUID] = Query([]),
) -> list[PlaceScheme]:
    feed = await service.get_user_feed(db_session, user, ignore_ids)
    return feed


@router.get(
    "/comments",
    response_model=list[PlaceComment]
)
async def comments(
        user: CurrentUserDep,
        db_session: DBSessionDep,
        place_id: uuid.UUID = Query(),
) -> list[PlaceComment]:
    return await service.get_comments(db_session, place_id)


@router.post(
    "/comment",
    response_model=PlaceComment
)
async def comment(
        user: CurrentUserDep,
        db_session: DBSessionDep,
        comment: PlaceCommentSchema,
) -> PlaceComment:
    try:
        return await service.add_comment(db_session, user.id, comment)
    except ValueError as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
