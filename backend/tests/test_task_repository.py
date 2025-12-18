import pytest
from oasst_backend.task_repository import validate_frontend_message_id
from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode


def test_validate_frontend_message_id_valid():
    """Test that a valid string ID passes validation."""
    validate_frontend_message_id("valid-id-123")


def test_validate_frontend_message_id_empty():
    """Test that an empty string raises an error."""
    with pytest.raises(OasstError) as excinfo:
        validate_frontend_message_id("")

    assert excinfo.value.error_code == OasstErrorCode.INVALID_FRONTEND_MESSAGE_ID
    assert "message_id must not be empty" in str(excinfo.value)


def test_validate_frontend_message_id_none():
    """Test that None raises an error."""
    with pytest.raises(OasstError) as excinfo:
        validate_frontend_message_id(None)

    assert excinfo.value.error_code == OasstErrorCode.INVALID_FRONTEND_MESSAGE_ID
    assert "message_id must be string" in str(excinfo.value)


def test_validate_frontend_message_id_wrong_type():
    """Test that a non-string type raises an error."""
    with pytest.raises(OasstError) as excinfo:
        validate_frontend_message_id(12345)

    assert excinfo.value.error_code == OasstErrorCode.INVALID_FRONTEND_MESSAGE_ID
    assert "message_id must be string" in str(excinfo.value)
