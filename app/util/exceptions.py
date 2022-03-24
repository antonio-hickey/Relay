from typing import Optional

from app.util.http_error_codes import HTTP_BAD_REQUEST, HTTP_CONFLICT


class UserException(Exception):
    error_description: str = ''

    def __init__(self, error_description: str, status_code: int = 400, data: Optional[dict] = None):
        super().__init__(error_description)
        self.status_code = status_code
        self.data = data
        self.error_description = error_description


class UsernameExistsException(UserException):
    def __init__(self, error_description: str) -> None:
        super().__init__(error_description=error_description, status_code=HTTP_CONFLICT)


class UserDoesNotExistException(UserException):
    def __init__(self, error_description: str) -> None:
        super().__init__(error_description=error_description, status_code=HTTP_BAD_REQUEST)
