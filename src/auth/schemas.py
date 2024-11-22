import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, constr


class Token(BaseModel):
    access_token: str
    token_type: str  # todo maybe make it Literal


class RegisterData(BaseModel):
    name: constr(min_length=2, max_length=127)
    email: EmailStr
    password: constr(min_length=6, max_length=511)


class LoginData(BaseModel):
    email: EmailStr
    password: constr(min_length=6, max_length=511)


class UserScheme(BaseModel):
    id: uuid.UUID
    email: EmailStr

    class Config:
        from_attributes = True


class UserSchemeDetailed(BaseModel):
    id: uuid.UUID
    email: EmailStr
    password: str

    class Config:
        from_attributes = True
