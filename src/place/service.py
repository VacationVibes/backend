from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from src.models import PlaceReactionModel, UserModel, PlaceModel, PlaceImageModel, PlaceTypeModel
from src.place.exceptions import InvalidPlaceException
from src.place.schemas import ReactionData, PlaceMin, PlaceImageMin, PlaceTypeMin, PlaceReactionMin
from src.schemas import PlaceScheme, PlaceReactionScheme, PlaceImageScheme, PlaceTypeScheme


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
    # SELECT place, place_reaction,
    #        array_agg(DISTINCT place_image) AS place_images,
    #        array_agg(DISTINCT place_type) AS place_types
    # FROM place_reaction
    # JOIN place ON place.id = place_reaction.place_id
    # JOIN place_image ON place.id = place_image.place_id
    # JOIN place_type ON place.id = place_type.place_id
    # WHERE place_reaction.user_id = 'd2200509-9ba5-4573-938f-330f690a0c08'::UUID
    # GROUP BY place.id, place_reaction.id;

    query = (
        select(
            PlaceModel,
            PlaceReactionModel,
            func.array_agg(
                func.distinct(PlaceImageModel.place_id, PlaceImageModel.image_url, PlaceImageModel.created_at)),
            func.array_agg(
                func.distinct(PlaceTypeModel.place_id, PlaceTypeModel.type, PlaceTypeModel.created_at))
        )
        .join(PlaceReactionModel)
        .join(PlaceImageModel)
        .join(PlaceTypeModel)
        .offset(offset)
        .limit(limit)
        .filter(PlaceReactionModel.user_id == user.id)
        .group_by(PlaceModel.id, PlaceReactionModel.id)
        .order_by(desc(PlaceReactionModel.created_at))
    )

    result = await db_session.execute(query)
    places = result.fetchall()

    return [
        PlaceScheme(
            id=place[0].id,
            name=place[0].name,
            place_id=place[0].place_id,
            latitude=place[0].latitude,
            longitude=place[0].longitude,
            created_at=place[0].created_at,
            reactions=[PlaceReactionScheme(
                id=place[1].id,
                reaction=place[1].reaction,
                created_at=place[1].created_at
            )],
            images=[
                PlaceImageScheme(
                    place_id=image[0],
                    image_url=image[1],
                    created_at=image[2],
                )
                for image in place[2]
            ],
            types=[
                PlaceTypeScheme(
                    place_id=type_[0],
                    type=type_[1],
                    created_at=type_[2],
                )
                for type_ in place[3]
            ],
        )
        for place in places
    ]


async def get_user_feed(db_session: AsyncSession, user: UserModel) -> list[PlaceScheme]:
    # todo implement collaborative filtering

    query = (
        select(PlaceModel)
        .options(
            selectinload(PlaceModel.images),
            selectinload(PlaceModel.types)
        )
        .filter(~PlaceModel.reactions.any(PlaceReactionModel.user_id == user.id))
        .limit(10)
    )

    result = await db_session.execute(query)
    places = result.unique().scalars().all()
    return [PlaceScheme.model_validate(place) for place in places]
    # return [PlaceScheme.model_validate({**place.__dict__, 'reactions': None}) for place in places]
