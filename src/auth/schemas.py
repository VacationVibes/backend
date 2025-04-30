from typing import Literal

from pydantic import BaseModel, EmailStr, constr


class Token(BaseModel):
    access_token: str
    token_type: Literal['Bearer']


class RegisterData(BaseModel):
    name: constr(min_length=2, max_length=127)
    email: EmailStr
    password: constr(min_length=6, max_length=511)


class LoginData(BaseModel):
    email: EmailStr
    password: constr(min_length=6, max_length=511)


class PasswordData(BaseModel):
    current_password: constr(min_length=6, max_length=511)
    new_password: constr(min_length=6, max_length=511)
