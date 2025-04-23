import math
import traceback
import uuid

from sqlalchemy import select, desc, func, case, and_
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

# Content-Based Recommendation System with TF-IDF Weighting
async def get_user_feed(db_session: AsyncSession, user: UserModel, ignore_ids: list[uuid.UUID]) -> list[PlaceScheme]:
    # Ignore overly common types that don't provide meaningful differentiation
    COMMON_TYPES = {"establishment", "point_of_interest", "tourist_attraction"}

    # Count the number of user reactions
    count_query = (
        select(func.count())
        .select_from(PlaceReactionModel)
        .filter(PlaceReactionModel.user_id == user.id)
    )
    count_result = await db_session.execute(count_query)
    reaction_count = count_result.scalar()

    # For new users with fewer than 50 reactions - show them high-rated unrated places
    if reaction_count < 50:
        query = (
            select(PlaceModel)
            .options(
                selectinload(PlaceModel.images),
                selectinload(PlaceModel.types)
            )
            .filter(~PlaceModel.reactions.any(PlaceReactionModel.user_id == user.id))
            .filter(~PlaceModel.id.in_(ignore_ids) if ignore_ids else True)
            .order_by(PlaceModel.rating.desc().nullslast())
            .limit(10)
        )
    else:
        # Get the total number of places for IDF calculation
        total_places_query = select(func.count()).select_from(PlaceModel)
        total_places_result = await db_session.execute(total_places_query)
        total_places = total_places_result.scalar()

        # Get count of places for each type (excluding common types)
        type_counts_query = (
            select(
                PlaceTypeModel.type,
                func.count().label('type_count')
            )
            .group_by(PlaceTypeModel.type)
            .filter(~PlaceTypeModel.type.in_(COMMON_TYPES))
        )
        type_counts_result = await db_session.execute(type_counts_query)
        type_counts = {row[0]: row[1] for row in type_counts_result.all()}

        # Get user preferences from their reactions
        user_preferences_query = (
            select(
                PlaceTypeModel.type,
                func.sum(
                    case(
                        (PlaceReactionModel.reaction == 'like', 1),
                        (PlaceReactionModel.reaction == 'dislike', -0.5),
                        else_=0
                    )
                ).label('raw_score')
            )
            .join(PlaceModel, PlaceTypeModel.place_id == PlaceModel.id)
            .join(PlaceReactionModel, PlaceReactionModel.place_id == PlaceModel.id)
            .where(
                and_(
                    PlaceReactionModel.user_id == user.id,
                    ~PlaceTypeModel.type.in_(COMMON_TYPES)  # Exclude common types
                )
            )
            .group_by(PlaceTypeModel.type)
        )

        user_preferences_result = await db_session.execute(user_preferences_query)
        user_preferences = user_preferences_result.all()

        # Calculate TF-IDF score for each type
        type_scores = []
        for type_name, raw_score in user_preferences:
            if type_name in type_counts and type_counts[type_name] > 0:
                # TF (term frequency) - how much the user likes this type
                # IDF (inverse document frequency) - how rare/specific the type is
                idf = math.log(total_places / type_counts[type_name])
                tf_idf_score = raw_score * idf
                type_scores.append((type_name, tf_idf_score))

        # Sort types by TF-IDF score and take top 5 with positive scores
        type_scores.sort(key=lambda x: x[1], reverse=True)
        top_types = [t[0] for t in type_scores[:5] if t[1] > 0]

        if not top_types:
            # Fallback: If no relevant types found, show high-rated places
            query = (
                select(PlaceModel)
                .options(
                    selectinload(PlaceModel.images),
                    selectinload(PlaceModel.types)
                )
                .filter(~PlaceModel.reactions.any(PlaceReactionModel.user_id == user.id))
                .filter(~PlaceModel.id.in_(ignore_ids) if ignore_ids else True)
                .order_by(PlaceModel.rating.desc().nullslast())
                .limit(10)
            )
        else:
            # Find places with relevant types
            # Use CTE to calculate relevance score for each place
            place_scores = (
                select(
                    PlaceTypeModel.place_id,
                    func.sum(
                        case(
                            *[(PlaceTypeModel.type == t, type_scores[i][1])
                              for i, t in enumerate(top_types) if i < len(type_scores)],
                            else_=0
                        )
                    ).label('relevance_score')
                )
                .filter(PlaceTypeModel.type.in_(top_types))
                .group_by(PlaceTypeModel.place_id)
                .cte('place_scores')
            )

            # Final query: join with relevance scores and sort
            query = (
                select(PlaceModel)
                .options(
                    selectinload(PlaceModel.images),
                    selectinload(PlaceModel.types)
                )
                .join(place_scores, PlaceModel.id == place_scores.c.place_id)
                .filter(~PlaceModel.reactions.any(PlaceReactionModel.user_id == user.id))
                .filter(~PlaceModel.id.in_(ignore_ids) if ignore_ids else True)
                .order_by(
                    place_scores.c.relevance_score.desc(),
                    PlaceModel.rating.desc().nullslast()
                )
                .limit(10)
            )

    result = await db_session.execute(query)
    places = result.unique().scalars().all()
    return [PlaceScheme.model_validate(place) for place in places]

async def get_comments(db_session: AsyncSession, place_id: uuid.UUID) -> list[PlaceComment]:
    query = (
        select(PlaceCommentModel)
        .options(selectinload(PlaceCommentModel.user))  # тянем user
        .where(PlaceCommentModel.place_id == place_id)
        .order_by(desc(PlaceCommentModel.created_at))
        .limit(10)
    )

    result = await db_session.execute(query)
    comments = result.unique().scalars().all()
    return [PlaceComment.model_validate(comment) for comment in comments]


async def add_comment(db_session: AsyncSession, user_id: uuid.UUID, comment: PlaceCommentSchema) -> None:
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
