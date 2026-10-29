from abc import ABC
from sqlmodel import Session


class AbstractRepo(ABC):
    def __init__(self, session: Session):
        self._session = session
