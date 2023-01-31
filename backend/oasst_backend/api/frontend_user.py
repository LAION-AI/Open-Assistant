# moved out of deps.py to avoid circular dependency with other injections
from typing import NamedTuple


class FrontendUserId(NamedTuple):
    auth_method: str
    username: str
