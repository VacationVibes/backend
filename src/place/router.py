from fastapi import APIRouter, Query

from src.auth.dependencies import CurrentUserDep
from src.place import service
from src.database import DBSessionDep

from src.place.schemas import ReactionData, SuccessResponse, ReactionsList, PlaceMin
from src.schemas import PlaceScheme

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
    response_model=ReactionsList
)
async def reaction(
        user: CurrentUserDep,
        db_session: DBSessionDep,
        offset: int = Query(0, ge=0),
        limit: int = Query(10, le=100)
) -> ReactionsList:
    reactions = await service.get_user_reactions(db_session, user, offset, limit)
    return ReactionsList(success=True, reactions=reactions)


@router.get(
    "/feed",
    response_model=list[PlaceMin]
)
async def reaction(
        user: CurrentUserDep,
        db_session: DBSessionDep
) -> list[PlaceScheme]:
    feed = await service.get_user_feed(db_session, user)
    return feed
