import json
from unittest import mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from oasst_backend.api.v1 import tasks
from oasst_backend.api.v1.tasks import TaskContext
from oasst_backend.prompt_repository import PromptRepository
from oasst_backend.task_repository import TaskRepository
from oasst_backend.tree_manager import TreeManager
from oasst_shared.schemas.protocol import TaskDone, TaskRequest
from starlette.status import HTTP_200_OK, HTTP_422_UNPROCESSABLE_ENTITY


class FakeApp:
    def __init__(self, app: FastAPI):
        self.app = app

        fake = mock.Mock(spec=TaskContext)
        fake.pr = mock.Mock(spec=PromptRepository)
        fake.tm = mock.Mock(spec=TreeManager)
        fake.tm.next_task.return_value = TaskDone(), "fake_tree_id", "fake_parent_message_id"
        fake.pr.task_repository = mock.Mock(spec=TaskRepository)

        def fake_factory(user):
            return fake

        self.app.dependency_overrides[tasks.get_task_context_factory] = lambda: fake_factory

        self.mock = fake


@pytest.fixture
def fake() -> FakeApp:
    app = FastAPI()
    app.include_router(tasks.router)
    return FakeApp(app)


@pytest.fixture
def client(fake: FakeApp) -> TestClient:
    return TestClient(fake.app)


def test_request_task_ok(client: TestClient, fake: FakeApp) -> None:
    response = client.post("/", data=TaskRequest().json())

    assert response.status_code == HTTP_200_OK
    fake.mock.pr.ensure_user_is_enabled.assert_called_once()
    fake.mock.tm.next_task.assert_called_once()
    fake.mock.pr.task_repository.store_task.assert_called_once()


@pytest.mark.parametrize(
    "payload",
    [
        {"user": {"id": "test", "display_name": "test", "auth_method": "unknown"}},
        {"type": "unknown"},
        {"collective": "unknown"},
    ],
)
def test_request_task_fails_on_malformed_payload(client: TestClient, fake: FakeApp, payload: dict) -> None:
    response = client.post("/", data=json.dumps(payload))

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    fake.mock.pr.ensure_user_is_enabled.assert_not_called()
    fake.mock.tm.next_task.assert_not_called()
    fake.mock.pr.task_repository.store_task.assert_not_called()
