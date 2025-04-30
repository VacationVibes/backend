from typing import Dict

from fastapi import APIRouter

from src.auth.dependencies import CurrentUserDep
from src.auth.schemas import RegisterData, LoginData, Token, PasswordData
from src.auth.exceptions import UserAlreadyExists, InvalidPassword
from src.auth import service
from src.database import DBSessionDep
from src.schemas import UserScheme

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
) -> Token:
    if await service.user_exists(db_session, register_data.email):
        raise UserAlreadyExists()

    user_model = await service.create_user(db_session, register_data)
    jwt_token = await service.validate_user(db_session, register_data.email, register_data.password)
    return Token(access_token=jwt_token, token_type="Bearer")


@router.get(
    "/me"
)
async def get_me(
        user: CurrentUserDep
) -> UserScheme:
    return user

@router.patch(
    "/password"
)
async def get_me(
        password_data: PasswordData,
        user: CurrentUserDep
) -> dict:
    if not service.verify_password(password_data.current_password, user.password):
        raise InvalidPassword

    return {"success": True}
