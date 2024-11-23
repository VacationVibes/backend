from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.models import PlaceReactionModel
from src.place.exceptions import InvalidPlaceException
from src.place.schemas import ReactionData, PlaceReactionScheme
from src.schemas import UserScheme


async def add_reaction(db_session: AsyncSession, reaction_data: ReactionData, user: UserScheme) -> None:
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


async def get_user_reactions(db_session: AsyncSession, user: UserScheme, offset: int, limit: int) -> list[
    PlaceReactionScheme]:
    query = (
        select(PlaceReactionModel)
        .filter(PlaceReactionModel.user_id == user.id)
        .offset(offset)
        .limit(limit)
        .order_by(desc(PlaceReactionModel.created_at))
    )

    result = await db_session.execute(query)
    places = result.scalars().all()
    return places
