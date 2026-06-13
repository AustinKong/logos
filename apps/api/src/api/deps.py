from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from api.db.database import get_db

DbSessionDep = Annotated[SQLAlchemySession, Depends(get_db)]
