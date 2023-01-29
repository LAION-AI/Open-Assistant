import json
from unittest import mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.status import HTTP_200_OK, HTTP_422_UNPROCESSABLE_ENTITY

import oasst_backend.api.deps
from oasst_backend.api.v1 import tasks
from oasst_shared.schemas.protocol import TaskDone, TaskRequest


class FakeApp:
    def __init__(self, app: FastAPI):
        self.app = app
        tree_manager = mock.Mock()
        tree_manager.next_task.return_value = TaskDone(), "fake_tree_id", "fake_parent_message_id"
        self.app.dependency_overrides[oasst_backend.api.deps.get_tree_manager] = lambda: tree_manager
        self.tree_manager = tree_manager


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
    fake.tree_manager.pr.ensure_user_is_enabled.assert_called_once()
    fake.tree_manager.next_task.assert_called_once()
    fake.tree_manager.pr.task_repository.store_task.assert_called_once()


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
    fake.tree_manager.pr.ensure_user_is_enabled.assert_not_called()
    fake.tree_manager.next_task.assert_not_called()
    fake.tree_manager.pr.task_repository.store_task.assert_not_called()
