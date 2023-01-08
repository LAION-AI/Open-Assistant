from .api_client import ApiClient
from .journal import Journal, JournalIntegration
from .message import Message
from .message_reaction import MessageReaction
from .message_tree_state import MessageTreeState
from .task import Task
from .text_labels import TextLabels
from .user import User
from .user_stats import UserStats

__all__ = [
    "ApiClient",
    "User",
    "UserStats",
    "Message",
    "MessageReaction",
    "MessageTreeState",
    "Task",
    "TextLabels",
    "Journal",
    "JournalIntegration",
]

# Add a docstring to provide an overview of the models
__doc__ = """
This module contains the SQLAlchemy models used in the application.

The models are:
- `ApiClient`: represents a client that consumes the API
- `User`: represents a user of the application
- `UserStats`: represents the statistics for a user
- `Message`: represents a message in the application
- `MessageReaction`: represents a reaction to a message
- `MessageTreeState`: represents the state of a message tree
- `Task`: represents a task in the application
- `TextLabels`: represents labels for text in the application
- `Journal`: represents a journal in the application
- `JournalIntegration`: represents an integration with a journaling service
"""
