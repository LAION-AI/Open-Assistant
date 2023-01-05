from oasst_backend.api.deps import api_auth
from oasst_backend.database import engine
from oasst_backend.prompt_repository import PromptRepository
from oasst_shared.schemas.protocol import User
from sqlmodel import Session

if __name__ == "__main__":
    db = Session(engine)
    api_client = api_auth("", db)

    new_user = User(id="randaom123", display_name="display", auth_method="discord")

    # First for that API Client, should create some random users
    pr = PromptRepository(db, api_client, user=new_user)
