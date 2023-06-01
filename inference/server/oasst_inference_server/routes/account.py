import fastapi
from fastapi import Depends
from oasst_inference_server import admin, auth, database, deps

router = fastapi.APIRouter(
    prefix="/account",
    tags=["account"],
)


@router.delete(path="/")
async def handle_account_deletion(
    user_id: str = Depends(dependency=auth.get_current_user_id),
    session: database.AsyncSession = Depends(dependency=deps.create_session),
) -> fastapi.Response:
    await admin.delete_user_from_db(session=session, user_id=user_id)
    return fastapi.Response(status_code=200)
