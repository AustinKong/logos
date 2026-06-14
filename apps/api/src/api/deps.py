from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session as SqlAlchemyDb

from api.db.database import get_db

DbDep = Annotated[SqlAlchemyDb, Depends(get_db)]
