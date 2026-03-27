from typing import Annotated
from fastapi import Depends
from sqlmodel import Session
from backend.db.database import get_session
from backend.logging_config import logger  # noqa: F401

SessionDep = Annotated[Session, Depends(get_session)]
