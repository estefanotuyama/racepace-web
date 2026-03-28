from typing import Annotated

from fastapi import Depends

from backend.repositories.driver import DriverRepoDep
from backend.schemas.read_driver import DriverResponse


class DriverService:
    def __init__(self, repo: DriverRepoDep):
        self.repo = repo

    def get_drivers(self, session_key: int) -> list[DriverResponse]:
        drivers = self.repo.get_drivers_from_session_key(session_key)
        return [
            DriverResponse(**d.model_dump(exclude={"id"}))
            for d in drivers
        ]


DriverServiceDep = Annotated[DriverService, Depends()]
