from typing import Annotated

from fastapi import Depends

from src.schemas import UserSchemeDetailed
from src.auth.service import get_current_user

CurrentUserDep = Annotated[UserSchemeDetailed, Depends(get_current_user)]
