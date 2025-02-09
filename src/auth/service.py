from datetime import datetime, timedelta
import argon2
import jwt
import uuid
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src import config
from argon2 import PasswordHasher
from src.auth.exceptions import UserDoesntExist, InvalidPassword
from src.auth.schemas import RegisterData
from src.database import get_db_session
from src.exceptions import InvalidCredentials, TokenExpired
from src.models import UserModel
from typing import Annotated

from src.schemas import UserSchemeDetailed

oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    scheme_name="JWT"
)

ph = PasswordHasher()


def verify_password(plain_password, hashed_password) -> bool:
    """
    Verify if the provided plain text password matches the hashed password.
    """
    return ph.verify(hashed_password, plain_password)


async def user_exists(db_session: AsyncSession, email: str) -> bool:
    user = (await db_session.execute(select(UserModel).where(UserModel.email == email))).scalar()
    return user is not None


async def validate_user(db_session: AsyncSession, email: str, password: str) -> str:
    user = await get_user_by_email(db_session, email)
    try:
        if verify_password(password, user.password):
            return create_access_token(user.id)

    except (argon2.exceptions.VerifyMismatchError, argon2.exceptions.VerificationError, argon2.exceptions.InvalidHashError):
        raise InvalidPassword()


async def get_user_by_id(db_session: AsyncSession, user_id: uuid.UUID) -> UserSchemeDetailed:
    user = (await db_session.scalars(select(UserModel).where(UserModel.id == user_id))).first()
    if not user:
        raise UserDoesntExist()
    return UserSchemeDetailed.model_validate(user)


async def get_user_by_email(db_session: AsyncSession, user_email: str) -> UserSchemeDetailed:
    user = (await db_session.scalars(select(UserModel).where(UserModel.email == user_email))).first()
    if not user:
        raise UserDoesntExist()
    return UserSchemeDetailed.model_validate(user)


def create_access_token(user_id: uuid.UUID, expiry_time: int = config.JWT_EXPIRY_TIME) -> str:
    to_encode = {"sub": str(user_id)}
    expire = datetime.now() + timedelta(minutes=expiry_time)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)],
                           db_session: AsyncSession = Depends(get_db_session)) -> UserSchemeDetailed:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        user_id = uuid.UUID(payload.get("sub"))
        if user_id is None:
            raise InvalidCredentials()
        return await get_user_by_id(db_session, user_id)
    except jwt.exceptions.ExpiredSignatureError:
        raise TokenExpired()
    except jwt.exceptions.DecodeError:
        raise InvalidCredentials()
    except ValueError:
        raise InvalidCredentials()


async def create_user(db_session: AsyncSession, register_data: RegisterData) -> UserSchemeDetailed:
    db_user = UserModel(
        name=register_data.name,
        email=register_data.email,
        password=ph.hash(register_data.password)
    )
    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)
    return UserSchemeDetailed.model_validate(db_user)
