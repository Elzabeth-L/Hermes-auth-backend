class AppException(Exception):
    status_code = 400
    message = "Application error"

    def __init__(self, message: str | None = None):
        self.message = message or self.message


class ConflictException(AppException):
    status_code = 409
    message = "Resource already exists"


class UnauthorizedException(AppException):
    status_code = 401
    message = "Invalid credentials"
