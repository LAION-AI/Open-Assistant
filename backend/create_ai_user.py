import argparse
import uuid
from pydantic import BaseModel
from sqlmodel import Session

from oasst_backend.database import engine
from oasst_backend.api.deps import create_api_client
from oasst_backend.models.api_client import ApiClient
from oasst_backend.models.user import User
from oasst_backend.user_repository import UserRepository
from oasst_shared.schemas import protocol as protocol_schema

CREATE_AI_USER_ID = uuid.UUID("2b4e4aa1-8746-4db3-b44c-90c30b316bf8")


class AIUserConfig(BaseModel):
    model: str


def create_ai_user(db: Session, api_client: ApiClient, config: AIUserConfig) -> User:
    """Create a new user with the AI role."""
    ur = UserRepository(db, api_client)
    user = protocol_schema.User(
        id=config.model,
        display_name=f"AI {config.model}",
        auth_method='system',
        ai_model=config.model,
    )
    user = ur.lookup_client_user(user, create_missing=True)
    return user


def main():
    parser = argparse.ArgumentParser(description="Create an AI user which can be used to generate messages.")
    parser.add_argument("--model", type=str, help="Model used for generating messages")
    args = parser.parse_args()
    with Session(engine) as db:
        api_client = db.query(ApiClient).filter(ApiClient.id == CREATE_AI_USER_ID).first()
        if not api_client:
            api_client = create_api_client(
                session=db,
                description="API client used for creating AI users",
                frontend_type="import",
                force_id=CREATE_AI_USER_ID,
            )
        create_ai_user(db, api_client, AIUserConfig(model=args.model))


if __name__ == "__main__":
    main()
