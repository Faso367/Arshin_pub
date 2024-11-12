from pydantic import BaseModel

class AnyErrorResponse(BaseModel):
    message: str


class CustomValidationErrorResponse(BaseModel):
    messages: list[str]


class AuthException(Exception):
    def __init__(self, message: str):
        self.message = message


class AuthExceptionResponse(BaseModel):
    message: str
    headers: dict = {"WWW-Authenticate": "Bearer"}