from unittest import mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from oasst_backend.api import deps
from oasst_backend.api.v1 import text_labels
from oasst_backend.schemas.text_labels import ValidLabelsResponse
from oasst_shared.schemas.protocol import TextLabel


@pytest.fixture
def app() -> FastAPI:
    fake_repo = mock.Mock()
    app = FastAPI()
    app.include_router(text_labels.router)
    app.dependency_overrides[deps.get_prompt_repository] = lambda: fake_repo
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


def test_get_valid_labels(client: TestClient) -> None:
    expected_labels = [(l.value, l.display_text, l.help_text) for l in TextLabel if l != TextLabel.fails_task]

    response = client.get("/valid_labels")
    valid_labels = ValidLabelsResponse.parse_obj(response.json()).valid_labels
    actual_labels = [(l.name, l.display_text, l.help_text) for l in valid_labels]

    assert expected_labels == actual_labels
