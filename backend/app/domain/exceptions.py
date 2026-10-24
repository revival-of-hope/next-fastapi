from sqlalchemy.exc import SQLAlchemyError


# 基类异常
class BaseException(Exception):
    pass


# DB异常
class DbException(BaseException):
    pass


class SQLError(DbException, SQLAlchemyError):
    pass


class AddError(SQLError):
    pass


class DeleteError(SQLError):
    pass


class CommitError(DbException, SQLAlchemyError):
    pass


# Repo异常
class RepoException(BaseException):
    pass


## UserRepo
class UserRecordNotFound(RepoException):
    pass


class UsersRecordNotFound(RepoException):
    pass


class UserRecordCreateFailed(RepoException):
    pass


class UserRecordDeleteError(RepoException):
    pass


class UserNameNotFound(RepoException):
    pass


class VerifyError(RepoException):
    pass


## ConversationRepo
class ConversationRecordNotFound(RepoException):
    pass


class ConversationsRecordNotFound(RepoException):
    pass


class ConversationRecordCreateError(RepoException):
    pass


# Service异常
class ServiceException(BaseException):
    pass
