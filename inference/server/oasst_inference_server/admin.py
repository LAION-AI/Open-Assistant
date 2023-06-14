"""Logic related to admin actions."""

import fastapi
from loguru import logger
from oasst_inference_server import database, models
from oasst_shared import utils as shared_utils


async def delete_user_from_db(session: database.AsyncSession, user_id: str):
    """Deletes a user."""
    logger.info(f"Deleting user {user_id}")
    user = await session.get(models.DbUser, user_id)
    if not user:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user.deleted = True

    # Anonymise user data
    user.display_name = shared_utils.DELETED_USER_DISPLAY_NAME
    # Ensure uniqueness
    user.provider_account_id = f"{shared_utils.DELETED_USER_ID_PREFIX}{user.id}"

    await session.commit()
