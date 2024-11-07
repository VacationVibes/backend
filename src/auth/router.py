from fastapi import APIRouter

from src.auth.dependencies import CurrentUserDep
from src.auth.schemas import RegisterData, LoginData, Token, UserScheme
from src.auth.exceptions import UserAlreadyExists
from src import config
from src.auth import service
from src.database import DBSessionDep
from src.exceptions import InvalidCredentials
import asyncio

router = APIRouter()


@router.post(
    "/login",
    response_model=Token
)
async def login(
        login_data: LoginData,
        db_session: DBSessionDep
) -> Token:
    jwt_token = await service.validate_user(db_session, login_data.email, login_data.password)
    return Token(access_token=jwt_token, token_type="Bearer")


@router.post(
    "/register",
    response_model=Token
)
async def register(
        register_data: RegisterData,
        db_session: DBSessionDep
):
    if await service.user_exists(db_session, register_data.email):
        raise UserAlreadyExists()

    user_model = await service.create_user(db_session, register_data)
    jwt_token = await service.validate_user(db_session, register_data.email, register_data.password)
    return Token(access_token=jwt_token, token_type="Bearer")


@router.get(
    "/me",
    response_model=UserScheme
)
async def get_me(
        user: CurrentUserDep
):
    return UserScheme.from_orm(user)
