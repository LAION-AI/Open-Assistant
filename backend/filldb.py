import random
import string
import string
import uuid
from datetime import datetime
from random import choice
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.ext.declarative import declarative_base
from oasst_backend.models import User, ApiClient, Message
import string
import uuid
from random import choice

# Connect to the database
engine = sa.create_engine("postgresql://postgres:postgres@localhost/postgres")
Session = sa.orm.sessionmaker(bind=engine)


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


# Insert the users
with Session() as db:

    api_client = create_random_api_client()
    db.add(api_client)
    db.commit()

    for i in range(1000):
        # Generate a random username
        username = "".join(choice(string.ascii_letters) for _ in range(10))
        user = User(
            username=username,
            auth_method="local",
            display_name=f"User {i}",
            api_client_id=api_client.id,
        )
        db.add(user)
    db.commit()


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


# Define a class to represent a message node in the tree
class MessageNode:
    def __init__(self, message_id, parent_id, text, role, api_client_id, user_id, message_tree_id, depth):
        self.id = message_id
        self.parent_id = parent_id
        self.text = text
        self.role = role
        self.api_client_id = api_client_id
        self.user_id = user_id
        self.message_tree_id = message_tree_id
        self.created_date = datetime.utcnow()
        self.payload_type = "text"
        self.payload = {"text": text}
        self.lang = "en-US"
        self.depth = depth
        self.children_count = 0
        self.deleted = False
        self.children = []


# Generate a random message tree with a given depth
def generate_random_message_tree(depth, api_client_id, user_id, message_tree_id):
    # Generate a random message id
    message_id = uuid.uuid4()
    # Randomly select a real sentence as the message text
    num_sentences = random.randint(8, 10)
    text = " ".join(random.sample(sentences, num_sentences))
    # Randomly assign a role to the message
    role = random.choice(["prompter", "assistant"])
    # Create a root node for the tree
    root = MessageNode(
        message_id,
        None,
        text,
        role,
        api_client_id,
        user_id,
        message_tree_id,
        0,
    )
    # Recursively generate child nodes for the root node
    generate_random_message_nodes(root, depth, api_client_id, user_id, message_tree_id)
    return root


# Recursively generate child nodes for a given message node
def generate_random_message_nodes(node, depth, api_client_id, user_id, message_tree_id):
    if depth > 0:
        # Generate a random number of child nodes
        num_children = random.randint(0, 5)
        for i in range(num_children):
            # Generate a random message id
            message_id = uuid.uuid4()
            # Randomly select a real sentence as the message text
            num_sentences = random.randint(5, 10)
            text = " ".join(random.sample(sentences, num_sentences))
            # Randomly assign a role to the message
            role = random.choice(["prompter", "assistant"])
            # Create a new message node
            child = Message(
                id=message_id,
                parent_id=node.id,
                message_tree_id=message_tree_id,
                user_id=user_id,
                role=role,
                api_client_id=api_client_id,
                frontend_message_id=str(uuid.uuid4()),
                payload_type="text",
                payload={"text": text},
                lang="en-US",
                depth=node.depth + 1,
                children_count=0,
                deleted=False,
            )
            # Add the child object to the parent node's children list
            node.children.append(child)
            # Recursively generate child nodes for the child node
            generate_random_message_nodes(child, depth - 1, api_client_id, user_id, message_tree_id)
