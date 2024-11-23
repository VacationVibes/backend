from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from src.models import PlaceReactionModel, UserModel, PlaceModel
from src.place.exceptions import InvalidPlaceException
from src.place.schemas import ReactionData
from src.schemas import PlaceScheme


async def add_reaction(db_session: AsyncSession, reaction_data: ReactionData, user: UserModel) -> None:
    db_reaction = PlaceReactionModel(
        place_id=reaction_data.place_id,
        user_id=user.id,
        reaction=reaction_data.reaction
    )
    db_session.add(db_reaction)
    try:
        await db_session.commit()
        await db_session.refresh(db_reaction)
    except IntegrityError:
        raise InvalidPlaceException()


async def get_user_reactions(db_session: AsyncSession, user: UserModel, offset: int, limit: int) -> list[PlaceScheme]:
    query = (
        select(PlaceModel)
        # .join(PlaceReactionModel)
        .filter(PlaceReactionModel.user_id == user.id)
        .options(selectinload(PlaceModel.reactions))
        # .distinct(PlaceReactionModel.id)
        .offset(offset)
        .limit(limit)
        .order_by(desc(PlaceReactionModel.created_at))
    )
    result = await db_session.execute(query)
    places = result.unique().scalars().all()
    return [PlaceScheme.model_validate(place) for place in places]


async def get_user_feed(db_session: AsyncSession, user: UserModel) -> list[PlaceScheme]:
    # todo implement collaborative filtering

    query = (
        select(PlaceModel)
        .filter(~PlaceModel.reactions.any(PlaceReactionModel.user_id == user.id))
        .limit(10)
    )

    result = await db_session.execute(query)
    places = result.unique().scalars().all()
    return [PlaceScheme.model_validate(place) for place in places]
    # return [PlaceScheme.model_validate({**place.__dict__, 'reactions': None}) for place in places]
