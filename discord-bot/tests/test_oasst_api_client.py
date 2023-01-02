from uuid import uuid4

import pytest
from bot.api_client import OasstApiClient
from oasst_shared.schemas import protocol as protocol_schema


@pytest.fixture
def oasst_api_client_mocked():
    client = OasstApiClient(backend_url="http://localhost:8080", api_key="123")
    yield client
    # TODO The fixture should close this connection, but there seems to be a bug
    # with async fixtures and pytest.
    # Since this only results in a warning, I'm leaving this for now.
    # await client.close()


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
                user=protocol_schema.User(
                    id="123",
                    display_name="lomz",
                    auth_method="discord",
                ),
            )
        )
        is not None
    )
