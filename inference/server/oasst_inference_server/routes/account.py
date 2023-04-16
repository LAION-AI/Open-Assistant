import fastapi
from fastapi import Depends
from oasst_inference_server import admin, auth, database, deps

router = fastapi.APIRouter(
    prefix="/account",
    tags=["account"],
)


@router.delete("/")
async def handle_account_deletion(
    user_id: str = Depends(auth.get_current_user_id),
    session: database.AsyncSession = Depends(deps.create_session),
) -> fastapi.Response:
    await admin.delete_user_from_db(session, user_id)
    return fastapi.Response(status_code=200)
