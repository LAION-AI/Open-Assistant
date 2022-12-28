# -*- coding: utf-8 -*-
import oasst_backend.error_codes as error_codes  # noqa: F401
from starlette.status import HTTP_400_BAD_REQUEST


class OasstError(Exception):
    """Base class for Open-Assistant exceptions."""

    message: str
    error_code: int
    http_status_code: int

    def __init__(self, message: str, error_code: int, http_status_code: int = HTTP_400_BAD_REQUEST):
        super().__init__(message, error_code, http_status_code)  # make excetpion picklable (fill args member)
        self.message = message
        self.error_code = error_code
        self.http_status_code = http_status_code

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f'{class_name}(message="{self.message}", error_code={self.error_code}, http_status_code={self.http_status_code})'
