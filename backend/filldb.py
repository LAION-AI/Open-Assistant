import random
import string
import uuid
import argparse
from random import choice
import sqlalchemy as sa
from oasst_backend.models import User, ApiClient
from oasst_backend.prompt_repository import PromptRepository, TaskRepository, UserRepository
from oasst_backend.tree_manager import TreeManager, TreeManagerConfiguration
from oasst_shared.schemas import protocol as protocol_schema
from oasst_backend.models import message_tree_state
from oasst_backend.api.v1.utils import prepare_conversation


def create_random_api_client(api_key_length: int = 512, description_length: int = 256, admin_email_length: int = 256):
    """Generates a random ApiClient object."""
    api_key = "".join(choice(string.ascii_letters + string.digits) for _ in range(api_key_length))
    description = "".join(choice(string.ascii_letters) for _ in range(description_length))
    admin_email = (
        "".join(choice(string.ascii_letters + string.digits) for _ in range(admin_email_length)) + "@example.com"
    )
    enabled = choice([True, False])
    trusted = choice([True, False])

    api_client = ApiClient(
        id=uuid.uuid4(),
        api_key=api_key,
        description=description,
        admin_email=admin_email,
        enabled=enabled,
        trusted=trusted,
    )
    return api_client


# Set up API client
def setup_api_client(session):
    api_client = create_random_api_client()
    with session as db:
        db.expire_on_commit = False
        db.add(api_client)
        db.commit()
    return api_client


def insert_users(user_repository, number_of_users: int = 1000):
    """Inserts users into the database."""
    for i in range(number_of_users):
        # Generate a random username
        username = "".join(choice(string.ascii_letters) for _ in range(10))
        print(username)
        user = protocol_schema.User(
            id=username,
            auth_method="local",
            display_name=f"User {i}",
        )
        user_repository.lookup_client_user(user)


def generate_random_message_tree(db, pr, tr, tm, api_client_id, user_id, depth, sentences):
    num_sentences = random.randint(5, 10)
    text = " ".join(random.sample(sentences, num_sentences))
    frontend_message_id = "".join(random.choices(string.ascii_lowercase, k=50))
    user_frontend_message_id = "".join(random.choices(string.ascii_lowercase, k=50))
    user_id = user_id
    message_tree_id = uuid.uuid4()
    task = tr.store_task(
        protocol_schema.InitialPromptTask(hint=""), message_tree_id=message_tree_id, parent_message_id=None
    )
    tr.bind_frontend_message_id(task.id, frontend_message_id)
    message = pr.store_text_reply(
        text, frontend_message_id, user_frontend_message_id, review_count=random.randint(0, 5), review_result=True
    )
    tm._insert_default_state(root_message_id=message_tree_id, state=message_tree_state.State.GROWING)
    db.commit()
    generate_random_message_nodes(
        db,
        pr,
        tr,
        tm,
        parent_message=message,
        depth=depth,
        api_client_id=api_client_id,
        user_id=user_id,
        message_tree_id=message_tree_id,
        sentences=sentences,
    )
    return message


def generate_random_message_nodes(
    db, pr, tr, tm, parent_message, depth, api_client_id, user_id, message_tree_id, sentences, ticker="assistant_reply"
):
    if depth > 0:
        num_children = random.randint(0, 3)
        for i in range(num_children):
            parent_message = pr.fetch_message_by_frontend_message_id(
                parent_message.frontend_message_id, fail_if_missing=True
            )
            conversation_messages = pr.fetch_message_conversation(parent_message)
            conversation = prepare_conversation(conversation_messages)
            current_message_tree = uuid.uuid4()
            if ticker == "assistant_reply":
                task = tr.store_task(
                    protocol_schema.AssistantReplyTask(conversation=conversation),
                    message_tree_id=current_message_tree,
                    parent_message_id=parent_message.id,
                )
                ticker = "prompter_reply"
            else:
                task = tr.store_task(
                    protocol_schema.PrompterReplyTask(conversation=conversation, hint=""),
                    message_tree_id=current_message_tree,
                    parent_message_id=parent_message.id,
                )
                ticker = "assistant_reply"
            frontend_message_id = "".join(random.choices(string.ascii_lowercase, k=20))
            user_frontend_message_id = "".join(random.choices(string.ascii_lowercase, k=50))
            tr.bind_frontend_message_id(task.id, frontend_message_id)
            num_sentences = random.randint(5, 10)
            text = " ".join(random.sample(sentences, num_sentences))
            message = pr.store_text_reply(
                text,
                frontend_message_id,
                user_frontend_message_id,
                review_count=random.randint(0, 5),
                review_result=True,
            )
            depth = depth - 1
            generate_random_message_nodes(
                db, pr, tr, tm, parent_message, depth, api_client_id, user_id, message_tree_id, sentences, ticker
            )


def main():

    # Define command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--users", type=int, help="Number of users to create", default=1000)
    parser.add_argument("--trees", type=int, help="Number of message trees to generate", default=100)
    args = parser.parse_args()

    # Get the number of users and message trees to generate
    num_users = args.users
    num_trees = args.trees

    # Connect to the database
    engine = sa.create_engine("postgresql://postgres:postgres@localhost/postgres")
    Session = sa.orm.sessionmaker(bind=engine)
    db = Session()
    # Setup API client
    api_client = setup_api_client(db)
    # Initialize Admin user
    admin = protocol_schema.User(
        id="admin",
        display_name="admin",
        auth_method="local",
    )
    ur = UserRepository(db=db, api_client=api_client)
    tr = TaskRepository(db=db, api_client=api_client, client_user=admin, user_repository=ur)
    # Initialize the prompt repository
    pr = PromptRepository(db=db, api_client=api_client, client_user=admin, user_repository=ur, task_repository=tr)
    tm = TreeManager(db, pr, TreeManagerConfiguration())
    # Insert users into the database
    insert_users(ur, number_of_users=num_users)
    # Insert message trees into the database
    sentences = [
        "Hello, how are you?",
        "I'm doing well, thank you.",
        "What do you like to do in your free time?",
        "I enjoy reading, watching movies, and going for walks.",
        "That sounds like a nice way to relax.",
        "Yes, it is. What about you?",
        "I like to play sports and spend time with my friends and family.",
        "That's great. Do you have any hobbies?",
        "I like to bake and cook. I also enjoy painting and drawing.",
        "Those are some interesting hobbies. Have you tried any new recipes lately?",
        "Yes, I made a new chocolate cake recipe that turned out really well. It was delicious!",
    ]
    # Pick the random user and insert the message tree
    for i in range(num_trees):
        user = random.choice(pr.db.query(User).all())
        generate_random_message_tree(db, pr, tr, tm, api_client.id, user.username, random.randint(0, 5), sentences)


if __name__ == "__main__":
    main()
