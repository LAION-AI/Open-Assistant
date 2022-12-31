import pytest
from bot.api_client import OasstApiClient

from oasst_shared.schemas import protocol as protocol_schema


@pytest.fixture
def oasst_api_client_mocked():
    client = OasstApiClient(backend_url="http://localhost:8080", api_key="123")
    yield client


@pytest.mark.asyncio
async def test_fetch_task(oasst_api_client_mocked: OasstApiClient):
    assert await oasst_api_client_mocked.fetch_task(task_type=protocol_schema.TaskRequestType.random) is not None
