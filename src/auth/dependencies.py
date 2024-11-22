from typing import Annotated

from fastapi import Depends

from src.auth.schemas import UserSchemeDetailed
from src.auth.service import get_current_user
from src.models import UserModel

# DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
CurrentUserDep = Annotated[UserSchemeDetailed, Depends(get_current_user)]
