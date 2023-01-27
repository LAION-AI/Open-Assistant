from typing import Any
from unittest import mock
from uuid import uuid4

import aiohttp
import pytest
from oasst_shared.api_client import OasstApiClient
from oasst_shared.exceptions import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema


@pytest.fixture
def oasst_api_client_mocked():
    """
    A an oasst_api_client pointed at the mocked backend.
    Relies on ./scripts/backend-development/start-mock-server.sh
    being run.
    """
    client = OasstApiClient(backend_url="http://localhost:8080", api_key="123")
    yield client
    # TODO The fixture should close this connection, but there seems to be a bug
    # with async fixtures and pytest.
    # Since this only results in a warning, I'm leaving this for now.
    # await client.close()


class MockClientSession(aiohttp.ClientSession):
    response: Any

    def set_response(self, response: Any):
        self.response = response

    async def post(self, *args, **kwargs):
        return self.response


@pytest.fixture
def mock_http_session():
    yield MockClientSession()


@pytest.fixture
def oasst_api_client_fake_http(mock_http_session):
    """
    An oasst_api_client that uses a mocked http session. No real requests are made.
    """
    client = OasstApiClient(backend_url="http://localhost:8080", api_key="123", session=mock_http_session)
    yield client


@pytest.mark.asyncio
@pytest.mark.parametrize("task_type", protocol_schema.TaskRequestType)
async def test_can_fetch_task(task_type: protocol_schema.TaskRequestType, oasst_api_client_mocked: OasstApiClient):
    assert await oasst_api_client_mocked.fetch_task(task_type=task_type) is not None


@pytest.mark.asyncio
async def test_can_ack_task(oasst_api_client_mocked: OasstApiClient):
    await oasst_api_client_mocked.ack_task(task_id=uuid4(), message_id="123")


@pytest.mark.asyncio
async def test_can_nack_task(oasst_api_client_mocked: OasstApiClient):
    await oasst_api_client_mocked.nack_task(task_id=uuid4(), reason="bad task")


@pytest.mark.asyncio
async def test_can_post_interaction(oasst_api_client_mocked: OasstApiClient):
    assert (
        await oasst_api_client_mocked.post_interaction(
            protocol_schema.TextReplyToMessage(
                type="text_reply_to_message",
                message_id="123",
                user_message_id="321",
                text="This is my reply",
                lang="en",
                user=protocol_schema.User(
                    id="123",
                    display_name="lomz",
                    auth_method="discord",
                ),
            )
        )
        is not None
    )


@pytest.mark.asyncio
async def test_can_handle_oasst_error_from_api(
    oasst_api_client_fake_http: OasstApiClient,
    mock_http_session: MockClientSession,
):
    # Return a 400 response with an OasstErrorResponse body
    response_body = protocol_schema.OasstErrorResponse(
        error_code=OasstErrorCode.GENERIC_ERROR,
        message="Some error",
    )
    status_code = 400

    mock_http_session.set_response(
        mock.AsyncMock(
            status=status_code,
            text=mock.AsyncMock(return_value=response_body.json()),
            json=mock.AsyncMock(return_value=response_body.dict()),
        )
    )

    with pytest.raises(OasstError):
        await oasst_api_client_fake_http.post("/some-path", data={})


@pytest.mark.asyncio
async def test_can_handle_unknown_error_from_api(
    oasst_api_client_fake_http: OasstApiClient,
    mock_http_session: MockClientSession,
):
    response_body = "Internal Server Error"
    status_code = 500

    mock_http_session.set_response(
        mock.AsyncMock(
            status=status_code,
            text=mock.AsyncMock(return_value=response_body),
            json=mock.AsyncMock(return_value=None),
        )
    )

    with pytest.raises(OasstError):
        await oasst_api_client_fake_http.post("/some-path", data={})
