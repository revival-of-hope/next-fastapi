from typing import Generic, TypeVar
from app.infra.repo import AbstractRepo

RepoT = TypeVar("RepoT", bound=AbstractRepo)


class BaseService(Generic[RepoT]):
    def __init__(self, repo: RepoT) -> None:
        self._repo = repo
