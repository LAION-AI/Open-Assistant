from unittest import mock
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from oasst_backend.api.v1 import text_labels
from oasst_backend.prompt_repository import PromptRepository
from oasst_backend.schemas.text_labels import ValidLabelsResponse
from oasst_shared.schemas.protocol import TextLabel, TextLabels, User
from starlette.status import HTTP_204_NO_CONTENT


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()
    app.include_router(text_labels.router, prefix="")
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


def test_get_valid_labels(client: TestClient) -> None:
    expected_labels = [(l.value, l.display_text, l.help_text) for l in TextLabel]

    actual_labels = [
        (l.name, l.display_text, l.help_text)
        for l in ValidLabelsResponse.parse_obj(client.get("/valid_labels").json()).valid_labels
    ]

    assert expected_labels == actual_labels


def test_label_text(client: TestClient) -> None:
    fake_repo = mock.MagicMock(spec=PromptRepository)

    def make_factory():
        nonlocal fake_repo

        def _inner(user: str):
            return fake_repo

        return _inner

    client.app.dependency_overrides[text_labels.prompt_repository_factory] = make_factory

    request = TextLabels(
        user=User(id="test", display_name="test", auth_method="local"),
        text="Knock, knock. Who's there? LLM.",
        labels={TextLabel.humor: 0.8, TextLabel.spam: 0.2},
        message_id=UUID(int=0),
        task_id=UUID(int=1),
    )

    response = client.post("/", content=request.json())

    assert response.status_code == HTTP_204_NO_CONTENT
    fake_repo.store_text_labels.assert_called_once()
    assert fake_repo.store_text_labels.call_args[0][0] == request
