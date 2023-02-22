from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from loguru import logger
from oasst_backend.api import deps
from oasst_backend.api.v1 import utils
from oasst_backend.models import ApiClient, MessageTreeState
from oasst_backend.prompt_repository import PromptRepository
from oasst_backend.schemas.message_tree import MessageTreeStateResponse
from oasst_backend.tree_manager import TreeManager
from oasst_backend.utils.database_utils import CommitMode, managed_tx_function
from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol
from sqlmodel import Session
from starlette.status import HTTP_204_NO_CONTENT

router = APIRouter()


@router.get("/", response_model=list[protocol.Message])
def query_messages(
    *,
    auth_method: Optional[str] = None,
    username: Optional[str] = None,
    api_client_id: Optional[str] = None,
    max_count: Optional[int] = Query(10, gt=0, le=1000),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    only_roots: Optional[bool] = False,
    desc: Optional[bool] = True,
    allow_deleted: Optional[bool] = False,
    lang: Optional[str] = None,
    frontend_user: deps.FrontendUserId = Depends(deps.get_frontend_user_id),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    """
    Query messages.
    """
    pr = PromptRepository(db, api_client, auth_method=frontend_user.auth_method, username=frontend_user.username)
    messages = pr.query_messages_ordered_by_created_date(
        auth_method=auth_method,
        username=username,
        api_client_id=api_client_id,
        desc=desc,
        limit=max_count,
        gte_created_date=start_date,
        lte_created_date=end_date,
        only_roots=only_roots,
        deleted=None if allow_deleted else False,
        lang=lang,
    )

    return utils.prepare_message_list(messages)


@router.get("/cursor", response_model=protocol.MessagePage)
def get_messages_cursor(
    *,
    before: Optional[str] = None,
    after: Optional[str] = None,
    user_id: Optional[UUID] = None,
    auth_method: Optional[str] = None,
    username: Optional[str] = None,
    api_client_id: Optional[str] = None,
    only_roots: Optional[bool] = False,
    include_deleted: Optional[bool] = False,
    max_count: Optional[int] = Query(10, gt=0, le=1000),
    desc: Optional[bool] = False,
    lang: Optional[str] = None,
    frontend_user: deps.FrontendUserId = Depends(deps.get_frontend_user_id),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    assert max_count is not None

    def split_cursor(x: str | None) -> tuple[datetime, UUID]:
        if not x:
            return None, None
        try:
            m = utils.split_uuid_pattern.match(x)
            if m:
                return datetime.fromisoformat(m[2]), UUID(m[1])
            return datetime.fromisoformat(x), None
        except ValueError:
            raise OasstError("Invalid cursor value", OasstErrorCode.INVALID_CURSOR_VALUE)

    if desc:
        gte_created_date, gt_id = split_cursor(before)
        lte_created_date, lt_id = split_cursor(after)
        query_desc = not (before is not None and not after)
    else:
        lte_created_date, lt_id = split_cursor(before)
        gte_created_date, gt_id = split_cursor(after)
        query_desc = before is not None and not after

    logger.debug(f"{desc=} {query_desc=} {gte_created_date=} {lte_created_date=}")

    qry_max_count = max_count + 1 if before is None or after is None else max_count

    pr = PromptRepository(db, api_client, frontend_user=frontend_user)
    items = pr.query_messages_ordered_by_created_date(
        user_id=user_id,
        auth_method=auth_method,
        username=username,
        api_client_id=api_client_id,
        gte_created_date=gte_created_date,
        gt_id=gt_id,
        lte_created_date=lte_created_date,
        lt_id=lt_id,
        only_roots=only_roots,
        deleted=None if include_deleted else False,
        desc=query_desc,
        limit=qry_max_count,
        lang=lang,
    )

    num_rows = len(items)
    if qry_max_count > max_count and num_rows == qry_max_count:
        assert not (before and after)
        items = items[:-1]

    if desc != query_desc:
        items.reverse()

    items = utils.prepare_message_list(items)
    n, p = None, None
    if len(items) > 0:
        if (num_rows > max_count and before) or after:
            p = str(items[0].id) + "$" + items[0].created_date.isoformat()
        if num_rows > max_count or before:
            n = str(items[-1].id) + "$" + items[-1].created_date.isoformat()
    else:
        if after:
            p = lte_created_date.isoformat() if desc else gte_created_date.isoformat()
        if before:
            n = gte_created_date.isoformat() if desc else lte_created_date.isoformat()

    order = "desc" if desc else "asc"
    return protocol.MessagePage(prev=p, next=n, sort_key="created_date", order=order, items=items)


@router.get("/{message_id}", response_model=protocol.Message)
def get_message(
    *,
    message_id: UUID,
    frontend_user: deps.FrontendUserId = Depends(deps.get_frontend_user_id),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    """
    Get a message by its internal ID.
    """
    pr = PromptRepository(db, api_client, frontend_user=frontend_user)
    message = pr.fetch_message(message_id)
    return utils.prepare_message(message)


@router.get("/{message_id}/conversation", response_model=protocol.Conversation)
def get_conv(
    *,
    message_id: UUID,
    frontend_user: deps.FrontendUserId = Depends(deps.get_frontend_user_id),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    """
    Get a conversation from the tree root and up to the message with given internal ID.
    """

    pr = PromptRepository(db, api_client, frontend_user=frontend_user)
    messages = pr.fetch_message_conversation(message_id)
    return utils.prepare_conversation(messages)


@router.get("/{message_id}/tree", response_model=protocol.MessageTree)
def get_tree(
    *,
    message_id: UUID,
    include_spam: Optional[bool] = True,
    include_deleted: Optional[bool] = False,
    frontend_user: deps.FrontendUserId = Depends(deps.get_frontend_user_id),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    """
    Get all messages belonging to the same message tree.
    """
    pr = PromptRepository(db, api_client, frontend_user=frontend_user)
    message = pr.fetch_message(message_id)
    review_result = None if include_spam else True
    deleted = None if include_deleted else False
    tree = pr.fetch_message_tree(message.message_tree_id, review_result=review_result, deleted=deleted)
    return utils.prepare_tree(tree, message.message_tree_id)


@router.get("/{message_id}/tree/state", response_model=MessageTreeStateResponse)
def get_message_tree_state(
    *,
    message_id: UUID,
    frontend_user: deps.FrontendUserId = Depends(deps.get_frontend_user_id),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
) -> MessageTreeStateResponse:
    pr = PromptRepository(db, api_client, frontend_user=frontend_user)
    message = pr.fetch_message(message_id=message_id, fail_if_missing=True)
    mts = pr.fetch_tree_state(message.message_tree_id)
    return MessageTreeStateResponse(
        message_tree_id=mts.message_tree_id,
        state=mts.state,
        active=mts.active,
        goal_tree_size=mts.goal_tree_size,
        max_children_count=mts.max_children_count,
        max_depth=mts.max_depth,
        origin=mts.origin,
    )


@router.put("/{message_id}/tree/state", response_model=MessageTreeStateResponse)
def put_message_tree_state(
    *,
    message_id: UUID,
    halt: bool,
    frontend_user: deps.FrontendUserId = Depends(deps.get_frontend_user_id),
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
) -> MessageTreeStateResponse:
    @managed_tx_function(CommitMode.COMMIT)
    def halt_tree_tx(session: deps.Session) -> MessageTreeState:
        pr = PromptRepository(session, api_client, frontend_user=frontend_user)
        tm = TreeManager(session, pr)
        return tm.halt_tree(message_id, halt=halt)

    mts = halt_tree_tx()
    return MessageTreeStateResponse(
        message_tree_id=mts.message_tree_id,
        state=mts.state,
        active=mts.active,
        goal_tree_size=mts.goal_tree_size,
        max_children_count=mts.max_children_count,
        max_depth=mts.max_depth,
        origin=mts.origin,
    )


@router.get("/{message_id}/children", response_model=list[protocol.Message])
def get_children(
    *,
    message_id: UUID,
    frontend_user: deps.FrontendUserId = Depends(deps.get_frontend_user_id),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    """
    Get all messages belonging to the same message tree.
    """
    pr = PromptRepository(db, api_client, frontend_user=frontend_user)
    messages = pr.fetch_message_children(message_id, review_result=None)
    return utils.prepare_message_list(messages)


@router.get("/{message_id}/descendants", response_model=protocol.MessageTree)
def get_descendants(
    *,
    message_id: UUID,
    frontend_user: deps.FrontendUserId = Depends(deps.get_frontend_user_id),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    """
    Get a subtree which starts with this message.
    """
    pr = PromptRepository(db, api_client, frontend_user=frontend_user)
    message = pr.fetch_message(message_id)
    descendants = pr.fetch_message_descendants(message)
    return utils.prepare_tree(descendants, message.id)


@router.get("/{message_id}/longest_conversation_in_tree", response_model=protocol.Conversation)
def get_longest_conv(
    *,
    message_id: UUID,
    frontend_user: deps.FrontendUserId = Depends(deps.get_frontend_user_id),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    """
    Get the longest conversation from the tree of the message.
    """
    pr = PromptRepository(db, api_client, frontend_user=frontend_user)
    message = pr.fetch_message(message_id)
    conv = pr.fetch_longest_conversation(message.message_tree_id)
    return utils.prepare_conversation(conv)


@router.get("/{message_id}/max_children_in_tree", response_model=protocol.MessageTree)
def get_max_children(
    *,
    message_id: UUID,
    frontend_user: deps.FrontendUserId = Depends(deps.get_frontend_user_id),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    """
    Get message with the most children from the tree of the provided message.
    """
    pr = PromptRepository(db, api_client, frontend_user=frontend_user)
    message = pr.fetch_message(message_id)
    message, children = pr.fetch_message_with_max_children(message.message_tree_id)
    return utils.prepare_tree([message, *children], message.id)


@router.delete("/{message_id}", status_code=HTTP_204_NO_CONTENT)
def mark_message_deleted(
    *,
    message_id: UUID,
    frontend_user: deps.FrontendUserId = Depends(deps.get_frontend_user_id),
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
    db: Session = Depends(deps.get_db),
):
    pr = PromptRepository(db, api_client, frontend_user=frontend_user)
    pr.mark_messages_deleted(message_id)


@router.post("/{message_id}/emoji", response_model=protocol.Message)
def post_message_emoji(
    *,
    message_id: UUID,
    request: protocol.MessageEmojiRequest,
    api_client: ApiClient = Depends(deps.get_api_client),
) -> protocol.Message:
    """
    Toggle, add or remove message emoji.
    """

    @managed_tx_function(CommitMode.COMMIT)
    def emoji_tx(session: deps.Session):
        pr = PromptRepository(session, api_client, client_user=request.user)
        return pr.handle_message_emoji(message_id, request.op, request.emoji)

    return utils.prepare_message(emoji_tx())
