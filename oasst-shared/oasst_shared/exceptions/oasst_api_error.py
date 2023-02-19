from enum import IntEnum
from http import HTTPStatus


class OasstErrorCode(IntEnum):
    """
    Error codes of the Open-Assistant backend API.

    Ranges:
         0-1000: general errors
      1000-2000: tasks endpoint
      2000-3000: prompt_repository, task_repository, user_repository
      3000-4000: external resources
    """

    # 0-1000: general errors
    GENERIC_ERROR = 0
    DATABASE_URI_NOT_SET = 1
    API_CLIENT_NOT_AUTHORIZED = 2
    ROOT_TOKEN_NOT_AUTHORIZED = 3
    DATABASE_MAX_RETRIES_EXHAUSTED = 4

    SORT_KEY_UNSUPPORTED = 100
    INVALID_CURSOR_VALUE = 101

    TOO_MANY_REQUESTS = 429

    SERVER_ERROR0 = 500
    SERVER_ERROR1 = 501

    INVALID_AUTHENTICATION = 600

    # 1000-2000: tasks endpoint
    TASK_INVALID_REQUEST_TYPE = 1000
    TASK_ACK_FAILED = 1001
    TASK_NACK_FAILED = 1002
    TASK_INVALID_RESPONSE_TYPE = 1003
    TASK_INTERACTION_REQUEST_FAILED = 1004
    TASK_GENERATION_FAILED = 1005
    TASK_REQUESTED_TYPE_NOT_AVAILABLE = 1006
    TASK_AVAILABILITY_QUERY_FAILED = 1007
    TASK_MESSAGE_TOO_LONG = 1008
    TASK_MESSAGE_DUPLICATED = 1009
    TASK_MESSAGE_TEXT_EMPTY = 1010
    TASK_MESSAGE_DUPLICATE_REPLY = 1011
    TASK_TOO_MANY_PENDING = 1012

    # 2000-3000: prompt_repository
    INVALID_FRONTEND_MESSAGE_ID = 2000
    MESSAGE_NOT_FOUND = 2001
    RATING_OUT_OF_RANGE = 2002
    INVALID_RANKING_VALUE = 2003
    INVALID_TASK_TYPE = 2004

    NO_MESSAGE_TREE_FOUND = 2006
    NO_REPLIES_FOUND = 2007
    INVALID_MESSAGE = 2008
    BROKEN_CONVERSATION = 2009
    TREE_IN_ABORTED_STATE = 2010
    CORRUPT_RANKING_RESULT = 2011
    AUTH_AND_USERNAME_REQUIRED = 2012

    TEXT_LABELS_WRONG_MESSAGE_ID = 2050
    TEXT_LABELS_INVALID_LABEL = 2051
    TEXT_LABELS_MANDATORY_LABEL_MISSING = 2052
    TEXT_LABELS_NO_SELF_LABELING = 2053
    TEXT_LABELS_DUPLICATE_TASK_REPLY = 2053

    TASK_NOT_FOUND = 2100
    TASK_EXPIRED = 2101
    TASK_PAYLOAD_TYPE_MISMATCH = 2102
    TASK_ALREADY_UPDATED = 2103
    TASK_NOT_ACK = 2104
    TASK_ALREADY_DONE = 2105
    TASK_NOT_COLLECTIVE = 2106
    TASK_NOT_ASSIGNED_TO_USER = 2106
    TASK_UNEXPECTED_PAYLOAD_TYPE_ = 2107

    # 3000-4000: external resources
    HUGGINGFACE_API_ERROR = 3001

    # 4000-5000: user
    USER_NOT_SPECIFIED = 4000
    USER_DISABLED = 4001
    USER_NOT_FOUND = 4002
    USER_HAS_NOT_ACCEPTED_TOS = 4003

    EMOJI_OP_UNSUPPORTED = 5000

    CACHED_STATS_NOT_AVAILABLE = 6000


class OasstError(Exception):
    """Base class for Open-Assistant exceptions."""

    message: str
    error_code: int
    http_status_code: HTTPStatus

    def __init__(self, message: str, error_code: OasstErrorCode, http_status_code: HTTPStatus = HTTPStatus.BAD_REQUEST):
        super().__init__(message, error_code, http_status_code)  # make exception picklable (fill args member)
        self.message = message
        self.error_code = error_code
        self.http_status_code = http_status_code

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f'{class_name}(message="{self.message}", error_code={self.error_code}, http_status_code={self.http_status_code})'
