from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session as SqlAlchemyDb

from api.db.database import get_db
from api.vector.database import VectorDatabase, get_vector_db

DbDep = Annotated[SqlAlchemyDb, Depends(get_db)]


VectorDbDep = Annotated[VectorDatabase, Depends(get_vector_db)]
