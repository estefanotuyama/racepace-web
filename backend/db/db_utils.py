import logging
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session
from backend.db.database import get_session

logger = logging.getLogger("racepace")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

SessionDep = Annotated[Session, Depends(get_session)]
