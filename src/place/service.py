import uuid

from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from src.models import PlaceReactionModel, UserModel, PlaceModel, PlaceImageModel, PlaceTypeModel, PlaceCommentModel
from src.place.exceptions import InvalidPlaceException
from src.place.schemas import ReactionData, PlaceMin, PlaceImageMin, PlaceTypeMin, PlaceReactionMin, PlaceCommentSchema
from src.schemas import PlaceScheme, PlaceReactionScheme, PlaceImageScheme, PlaceTypeScheme, PlaceComment


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
        select(
            PlaceModel,
            PlaceReactionModel,
            func.array(
                select(
                    func.row(PlaceImageModel.place_id, PlaceImageModel.image_url, PlaceImageModel.created_at)
                ).where(PlaceImageModel.place_id == PlaceModel.id)
                .scalar_subquery()
            ).label("images"),
            func.array(
                select(
                    func.row(PlaceTypeModel.place_id, PlaceTypeModel.type, PlaceTypeModel.created_at)
                ).where(PlaceTypeModel.place_id == PlaceModel.id)
                .scalar_subquery()
            ).label("types")
        )
        .join(PlaceReactionModel)
        .offset(offset)
        .limit(limit)
        .filter(PlaceReactionModel.user_id == user.id)
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


# async def get_user_reactions(db_session: AsyncSession, user: UserModel, offset: int, limit: int) -> list[PlaceScheme]:
#     # 1. Запрашиваем только места и реакции пользователя (без JOIN-ов)
#     query = (
#         select(PlaceModel)
#         .join(PlaceReactionModel)
#         .filter(PlaceReactionModel.user_id == user.id)
#         .options(selectinload(PlaceModel.reactions))
#         .order_by(desc(PlaceReactionModel.created_at))
#         .offset(offset)
#         .limit(limit)
#     )
#
#     result = await db_session.execute(query)
#     places = result.scalars().all()  # Без fetchall() - работаем с объектами
#
#     # 2. Загружаем связанные данные отдельно
#     place_ids = [place.id for place in places]
#
#     # 2.1 Загружаем изображения одним запросом
#     images_query = select(PlaceImageModel).filter(PlaceImageModel.place_id.in_(place_ids))
#     images_result = await db_session.execute(images_query)
#     images = images_result.scalars().all()
#
#     # 2.2 Загружаем типы одним запросом
#     types_query = select(PlaceTypeModel).filter(PlaceTypeModel.place_id.in_(place_ids))
#     types_result = await db_session.execute(types_query)
#     types = types_result.scalars().all()
#
#     # 3. Группируем связанные данные по place_id (оптимизируем доступ)
#     images_by_place = {}
#     for image in images:
#         images_by_place.setdefault(image.place_id, []).append(image)
#
#     types_by_place = {}
#     for type_ in types:
#         types_by_place.setdefault(type_.place_id, []).append(type_)
#
#     # 4. Собираем ответ
#     return [
#         PlaceScheme(
#             id=place.id,
#             name=place.name,
#             place_id=place.place_id,
#             latitude=place.latitude,
#             longitude=place.longitude,
#             created_at=place.created_at,
#             reactions=[PlaceReactionScheme(
#                 id=reaction.id,
#                 reaction=reaction.reaction,
#                 created_at=reaction.created_at
#             ) for reaction in place.reactions],
#             images=[
#                 PlaceImageScheme(
#                     place_id=image.place_id,
#                     image_url=image.image_url,
#                     created_at=image.created_at
#                 ) for image in images_by_place.get(place.id, [])
#             ],
#             types=[
#                 PlaceTypeScheme(
#                     place_id=type_.place_id,
#                     type=type_.type,
#                     created_at=type_.created_at
#                 ) for type_ in types_by_place.get(place.id, [])
#             ],
#         )
#         for place in places
#     ]

async def get_user_feed(db_session: AsyncSession, user: UserModel, ignore_ids: list[uuid.UUID]) -> list[PlaceScheme]:
    # todo implement collaborative filtering

    query = (
        select(PlaceModel)
        .options(
            selectinload(PlaceModel.images),
            selectinload(PlaceModel.types)
        )
        .filter(~PlaceModel.reactions.any(PlaceReactionModel.user_id == user.id))
        .filter(~PlaceModel.id.in_(ignore_ids))
        .limit(10)
    )

    result = await db_session.execute(query)
    places = result.unique().scalars().all()
    return [PlaceScheme.model_validate(place) for place in places]
    # return [PlaceScheme.model_validate({**place.__dict__, 'reactions': None}) for place in places]


async def get_comments(db_session: AsyncSession, place_id: uuid.UUID) -> list[PlaceComment]:
    query = (
        select(PlaceCommentModel)
        .where(PlaceCommentModel.place_id == place_id)
        .order_by(desc(PlaceCommentModel.created_at))
        .limit(10)
    )

    result = await db_session.execute(query)
    places = result.unique().scalars().all()
    return [PlaceComment.model_validate(place) for place in places]


async def add_comment(db_session: AsyncSession, user_id: uuid.UUID, comment: PlaceCommentSchema) -> PlaceComment:
    new_comment = PlaceCommentModel(
        place_id=comment.place_id,
        user_id=user_id,
        comment=comment.comment,
        rating=comment.rating
    )

    db_session.add(new_comment)
    try:
        await db_session.commit()
    except IntegrityError:
        raise ValueError("Error inserting the comment")

    return PlaceComment.model_validate(new_comment)
