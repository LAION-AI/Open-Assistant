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

    def fill_api_client(self, num_api_client: int = 10):
        """Fill the database with api clients

        Args:
            num_api_client (int, optional): the number of api clients that we want to create. Defaults to 10.
        """

        # Create the Session to the database
        with Session(self.db_engine) as db:

            # For the range of the api clients we want to create
            for num in range(num_api_client):

                # Create a new ApiClient
                random_api_client = self._create_random_api_client()

                # Store the API key created
                self.api_keys.append(random_api_client.api_key)

                # Store this new ApiClient in the database
                db.add(random_api_client)
                db.commit()
                db.refresh(random_api_client)

        # Return all the api clients created
        return self.api_keys

    def fill_users(self):
        pass

    def _create_random_api_client(
        self, api_key_length: str = 512, description_length: str = 256, admin_email_length: str = 256
    ):
        """Create Random Api Client values"""

        # Two random booleans for enabled & trusted
        enabled, trusted = self._create_random_bool(2)

        # Create random strings with characters & digits
        api_key = self._create_random_str(api_key_length)
        description = self._create_random_str(description_length)
        admin_email = self._create_random_str(admin_email_length) + "@example.com"

        # Create the API Client object
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
    def _create_random_str(length: str) -> str:
        """Generator of a random string

        Args:
            length (str): the length of the string we want to generate

        Returns:
            str: the random string generated
        """

        return "".join(choice(string.ascii_letters + string.digits) for _ in range(length))

    @staticmethod
    def _create_random_bool(length: int) -> List[bool]:
        """Create a list of booleans for a certain length.

        Args:
            length (int): the length of the list that we want in response

        Returns:
            list[bool]: generator of the list of booleans
        """

        return (choice([True, False]) for idx in range(length))


if __name__ == "__main__":
    fill_db = FillDb(engine)
    fill_db.fill_api_client()
    print(fill_db.api_keys)
