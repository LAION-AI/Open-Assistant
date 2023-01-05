import random
import string
import uuid
from random import choice
from typing import List

from oasst_backend.database import engine
from oasst_backend.models import ApiClient
from sqlmodel import Session


class FillDb:
    """Class object which fills the database: Api Client, Users & Messages."""

    def __init__(self, db_engine, seed: int = 0):
        # The database engine
        self.db_engine = db_engine

        # Store the generated api keys
        self.api_keys: List[str] = []

        # Seed to make sure values are reproducible
        random.seed(seed)

    def fill_api_client(
        self,
    ):

        with Session(self.db_engine) as db:
            random_api_client = self._create_random_api_client()

            # Store the API key created
            self.api_keys.append(random_api_client.api_key)

            db.add(random_api_client)
            db.commit()
            db.refresh(random_api_client)

            pass

    def fill_users(self):
        pass

    def _create_random_api_client(
        self, api_key_length: str = 512, description_length: str = 256, admin_email_length: str = 256
    ):
        """Create Random Api Client values"""

        enabled, trusted = self._create_random_bool(2)
        api_key = self._create_random_str(api_key_length)
        description = self._create_random_str(description_length)
        admin_email = self._create_random_str(admin_email_length) + "@example.com"

        api_client = ApiClient(
            id=uuid.uuid4(),
            api_key=api_key,
            description=description,
            admin_email=admin_email,
            enabled=enabled,
            trusted=trusted,
        )

        return api_client

    @staticmethod
    def _create_random_str(length: str):
        return "".join(choice(string.ascii_letters + string.digits) for _ in range(length))

    @staticmethod
    def _create_random_bool(length: int) -> List[bool]:
        """Create a list of booleans for a certain length.

        Args:
            length (int): the length of the list that we want in response

        Returns:
            Generator: generator of the list of booleans
        """

        return (choice([True, False]) for idx in range(length))


if __name__ == "__main__":
    fill_db = FillDb(engine)
    fill_db.fill_api_client()
    print(fill_db.api_keys)
