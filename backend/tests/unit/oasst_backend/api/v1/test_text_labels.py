from typing import Generator

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine

from oasst_backend.api.v1 import text_labels
from oasst_backend.schemas.text_labels import ValidLabelsResponse


def get_db() -> Generator:
    with Session(create_engine("sqlite://")) as db:
        yield db


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()
    app.include_router(text_labels.router, prefix="/text_labels")
    app.dependency_overrides[text_labels.deps.get_db] = get_db
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


def test_get_valid_labels(client: TestClient) -> None:
    response = ValidLabelsResponse.parse_obj(client.get("/text_labels/valid_labels").json())
    assert response.valid_labels
