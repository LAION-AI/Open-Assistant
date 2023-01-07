import argparse
import random
import string
import uuid
from random import choice
from typing import List

from oasst_backend.api.deps import api_auth
from oasst_backend.database import engine
from oasst_backend.models import ApiClient
from oasst_backend.prompt_repository import PromptRepository
from oasst_shared.schemas.protocol import User as ProtocolUser
from sqlmodel import Session


class FillDb:
    """Class object which fills the database: Api Client, Users & Messages."""

    def __init__(self, db_engine, num_api_clients: int = 10, num_users: int = 10, use_seed: bool = True, seed: int = 0):
        # The database engine
        self.db_engine = db_engine

        # Store the generated api keys
        self.api_keys: List[str] = []
        self.users: List[ProtocolUser] = []

        # The amount of data we want to produce
        self._num_api_clients = num_api_clients
        self._num_users = num_users

        # Seed to make sure values are reproducible
        if use_seed:
            random.seed(seed)

    def fill_api_client(self):
        """Fill the database with api clients

        Args:
            num_api_client (int, optional): the number of api clients that we want to create. Defaults to 10.
        """

        # Create the Session to the database
        with Session(self.db_engine) as db:

            # For the range of the api clients we want to create
            for _ in range(self._num_api_clients):

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
        """Fill with new users that have the API clients."""

        with Session(engine) as db:
            for _ in range(self._num_users):
                # Get the keys that we will use for that user
                api_key = self._get_random_api_client_key()
                api_client = self._get_api_auth(api_key, db)

                random_user = self._create_random_user()
                self.users.append(random_user)

                # First for that API Client, should create some random users
                PromptRepository(db, api_client, user=random_user)

        return self.users

    def _create_random_user(
        self,
        id_length: int = 56,
        display_name_length: int = 128,
    ):
        id = self._create_random_str(id_length)
        display_name = self._create_random_str(display_name_length)
        auth_method = self._create_random_auth_method()

        return ProtocolUser(id=id, display_name=display_name, auth_method=auth_method)

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

    def _get_random_api_client_key(self):
        """Return a random api client key from the ones that we already created.

        Returns:
            api_key: api key
        """

        return choice(self.api_keys)

    def _get_api_auth(self, api_key: str, db: Session) -> ApiClient:
        """Get the api auth based on the api key from the database.

        Args:
            api_key (str): the key from the api client.
            db (Session): the database session

        Returns:
            ApiClient: the api client that has this key
        """

        return api_auth(api_key, db)

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

        return (choice([True, False]) for _ in range(length))

    @staticmethod
    def _create_random_auth_method() -> str:
        """Create a random auth method: {discord, local}"""

        return choice(["discord", "local"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Fill Database",
        description="Fill the database with mock data generated randomly",
    )

    parser.add_argument("--api_client", type=int, default=1, help="Amount of API Clients that we want to create")

    parser.add_argument("--users", type=int, default=1, help="Amount of Users that we want to create")

    parser.add_argument("--seed", type=int, default=0, help="The value we want to use as seed")

    parser.add_argument(
        "--use_seed", type=bool, default=True, help="Whether we want to use seed for the random messages"
    )

    # Parse the arguments
    args = parser.parse_args()

    api_client = args.api_client
    users = args.users
    use_seed = args.use_seed
    seed = args.seed

    fill_db = FillDb(engine, api_client, users, use_seed=use_seed, seed=seed)

    fill_db.fill_api_client()
    fill_db.fill_users()
