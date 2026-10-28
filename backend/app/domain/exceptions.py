# 基类异常
class BaseException(Exception):
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


class PasswordMatchError(RepoException):
    pass


## ConversationRepo
class ConversationRecordNotFound(RepoException):
    pass


class ConversationsRecordNotFound(RepoException):
    pass


class ConversationRecordCreateError(RepoException):
    pass


class ConversationTitleUpdateError(RepoException):
    pass


class MessageRecordCreateError(RepoException):
    pass


class MessageRecordNotFound(RepoException):
    pass


# Service异常
class ServiceException(BaseException):
    pass


## UserService


class UserNotFound(ServiceException):
    pass


class UsersNotFound(ServiceException):
    pass


class UserCreateError(ServiceException):
    pass


class UserDeleteError(ServiceException):
    pass


class UserNotAdmin(ServiceException):
    pass


## ChatService
class MessagesNotFound(ServiceException):
    pass


class MessageCreateError(ServiceException):
    pass


class ConversationNotFound(ServiceException):
    pass


class ConversationCreateError(ServiceException):
    pass


class TitleUpdateError(ServiceException):
    pass


class UsageUpdateError(ServiceException):
    pass


class UsagesNotFound(ServiceException):
    pass


class ChatSaveError(ServiceException):
    pass
