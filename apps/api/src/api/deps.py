from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.database import get_db
from api.vector.database import VectorDatabase, get_vector_db

DbDep = Annotated[AsyncSession, Depends(get_db)]


VectorDbDep = Annotated[VectorDatabase, Depends(get_vector_db)]
