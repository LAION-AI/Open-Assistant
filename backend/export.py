import argparse
from pathlib import Path
from typing import List, Optional
from uuid import UUID

import sqlalchemy as sa
from loguru import logger
from oasst_backend.database import engine
from oasst_backend.models import Message, MessageTreeState, TextLabels
from oasst_backend.models.message_tree_state import State as TreeState
from oasst_backend.utils import tree_export
from oasst_shared.schemas.protocol import TextLabel
from sqlmodel import Session, func, not_


def fetch_tree_ids(
    db: Session,
    state_filter: Optional[TreeState] = None,
    lang: Optional[str] = None,
) -> list[tuple[UUID, TreeState]]:
    tree_qry = (
        db.query(MessageTreeState)
        .select_from(MessageTreeState)
        .join(Message, MessageTreeState.message_tree_id == Message.id)
    )

    if lang is not None:
        tree_qry = tree_qry.filter(Message.lang == lang)

    if state_filter:
        tree_qry = tree_qry.filter(MessageTreeState.state == state_filter)

    return [(tree.message_tree_id, tree.state) for tree in tree_qry]


def fetch_tree_messages(
    db: Session,
    message_tree_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    deleted: bool = None,
    prompts_only: bool = False,
    lang: Optional[str] = None,
    review_result: Optional[bool] = None,
) -> List[Message]:
    qry = db.query(Message)

    if message_tree_id:
        qry = qry.filter(Message.message_tree_id == message_tree_id)
    if user_id:
        qry = qry.filter(Message.user_id == user_id)
    if deleted is not None:
        qry = qry.filter(Message.deleted == deleted)
    if prompts_only:
        qry = qry.filter(Message.parent_id.is_(None))
    if lang:
        qry = qry.filter(Message.lang == lang)
    if review_result is False:
        qry = qry.filter(not_(Message.review_result), Message.review_count > 2)
    elif review_result is True:
        qry = qry.filter(Message.review_result)

    return qry.all()


def fetch_tree_messages_and_avg_labels(
    db: Session,
    message_tree_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    deleted: bool = None,
    prompts_only: bool = False,
    lang: Optional[str] = None,
    review_result: Optional[bool] = None,
) -> List[Message]:

    args = [Message]

    for l in TextLabel:
        args.append(func.avg(TextLabels.labels[l].cast(sa.Float)).label(l.value))
        args.append(func.count(TextLabels.labels[l]).label(l.value + "_count"))

    qry = db.query(*args).select_from(Message).join(TextLabels, Message.id == TextLabels.message_id)
    if message_tree_id:
        qry = qry.filter(Message.message_tree_id == message_tree_id)
    if user_id:
        qry = qry.filter(Message.user_id == user_id)
    if deleted is not None:
        qry = qry.filter(Message.deleted == deleted)
    if prompts_only:
        qry = qry.filter(Message.parent_id.is_(None))
    if lang:
        qry = qry.filter(Message.lang == lang)
    if review_result is False:
        qry = qry.filter(not_(Message.review_result), Message.review_count > 2)
    elif review_result is True:
        qry = qry.filter(Message.review_result)

    qry = qry.group_by(Message.id)

    return qry.all()


def export_trees(
    db: Session,
    export_file: Optional[Path] = None,
    use_compression: bool = False,
    deleted: bool = False,
    user_id: Optional[UUID] = None,
    prompts_only: bool = False,
    state_filter: Optional[TreeState] = None,
    lang: Optional[str] = None,
    review_result: Optional[bool] = None,
    export_labels: bool = False,
) -> None:
    message_labels: dict[UUID, tree_export.LabelValues] = {}
    if user_id:
        # when filtering by user we don't have complete message trees, export as list
        result = fetch_tree_messages_and_avg_labels(
            db,
            user_id=user_id,
            deleted=deleted,
            prompts_only=prompts_only,
            lang=lang,
            review_result=review_result,
        )

        messages: list[Message] = []
        for r in result:
            msg = r["Message"]
            messages.append(msg)
            if export_labels:
                labels: tree_export.LabelValues = {
                    l.value: tree_export.LabelAvgValue(value=r[l.value], count=r[l.value + "_count"])
                    for l in TextLabel
                    if r[l.value] is not None
                }
                message_labels[msg.id] = labels

        tree_export.write_messages_to_file(export_file, messages, use_compression, labels=message_labels)
    else:
        message_tree_ids = fetch_tree_ids(db, state_filter, lang=lang)

        message_trees: list[list[Message]] = []

        for tree_id, _ in message_tree_ids:
            if export_labels:
                result = fetch_tree_messages_and_avg_labels(
                    db,
                    message_tree_id=tree_id,
                    deleted=deleted,
                    prompts_only=prompts_only,
                    lang=None,  # pass None here, trees were selected based on lang of prompt
                    review_result=review_result,
                )

                messages: list[Message] = []
                for r in result:
                    msg = r["Message"]
                    messages.append(msg)
                    labels: tree_export.LabelValues = {
                        l.value: tree_export.LabelAvgValue(value=r[l.value], count=r[l.value + "_count"])
                        for l in TextLabel
                        if r[l.value] is not None
                    }
                    message_labels[msg.id] = labels

                message_trees.append(messages)
            else:
                messages = fetch_tree_messages(
                    db,
                    message_tree_id=tree_id,
                    deleted=deleted,
                    prompts_only=prompts_only,
                    lang=None,  # pass None here, trees were selected based on lang of prompt
                    review_result=review_result,
                )
                message_trees.append(messages)

        if review_result is False or deleted is True:
            # when exporting filtered we don't have complete message trees, export as list
            messages = [m for t in message_trees for m in t]  # flatten message list
            tree_export.write_messages_to_file(export_file, messages, use_compression, labels=message_labels)
        else:
            trees_to_export: List[tree_export.ExportMessageTree] = []

            for (message_tree_id, message_tree_state), message_tree in zip(message_tree_ids, message_trees):
                if len(message_tree) > 0:
                    try:
                        t = tree_export.build_export_tree(
                            message_tree_id=message_tree_id,
                            message_tree_state=message_tree_state,
                            messages=message_tree,
                            labels=message_labels,
                        )
                        if prompts_only:
                            t.prompt.replies = None
                        trees_to_export.append(t)
                    except Exception as ex:
                        logger.warning(f"Corrupted tree: {message_tree_id} ({ex})")

            tree_export.write_trees_to_file(export_file, trees_to_export, use_compression)


def validate_args(args):
    if args.deleted_only:
        args.include_deleted = True

    args.use_compression = args.export_file is not None and ".gz" in args.export_file

    if args.state and args.user is not None:
        raise ValueError("Cannot use --state when specifying a user ID")

    if args.export_file is None:
        logger.warning("No export file provided, output will be sent to STDOUT")


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--export-file",
        type=str,
        help="Name of file to export trees to. If not provided, output will be sent to STDOUT",
    )
    parser.add_argument(
        "--include-deleted",
        action="store_true",
        help="Include deleted messages in export",
    )
    parser.add_argument(
        "--deleted-only",
        action="store_true",
        help="Export only deleted messages (implies --include-deleted)",
    )
    parser.add_argument(
        "--include-spam",
        action="store_true",
        help="Export including messages with negative review result.",
    )
    parser.add_argument(
        "--spam-only",
        action="store_true",
        help="Export only messages with negative review result (implies --include-spam).",
    )
    parser.add_argument(
        "--user",
        type=str,
        help="Only export trees involving the user with the specified ID. Incompatible with --state.",
    )
    parser.add_argument(
        "--state",
        type=str,
        help="all|prompt_lottery_waiting|growing|ready_for_export|aborted_low_grade|halted_by_moderator|backlog_ranking",
    )
    parser.add_argument(
        "--lang",
        type=str,
        help="Filter message trees by language code (BCP 47)",
    )
    parser.add_argument(
        "--prompts-only",
        action="store_true",
        help="Export a list of initial prompt messages",
    )
    parser.add_argument(
        "--export-labels",
        action="store_true",
        help="Include average label values for messages",
    )

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    validate_args(args)

    state_filter: Optional[TreeState] = None
    if args.state is None:
        state_filter = TreeState.READY_FOR_EXPORT
    elif args.state != "all":
        state_filter = TreeState(args.state)

    deleted: Optional[bool] = False
    if args.include_deleted:
        deleted = None
    if args.deleted_only:
        deleted = True

    review_result: Optional[bool] = True
    if args.include_spam:
        review_result = None
    if args.spam_only:
        review_result = False

    with Session(engine) as db:
        export_trees(
            db,
            Path(args.export_file) if args.export_file is not None else None,
            use_compression=args.use_compression,
            deleted=deleted,
            user_id=UUID(args.user) if args.user is not None else None,
            prompts_only=args.prompts_only,
            state_filter=state_filter,
            lang=args.lang,
            review_result=review_result,
            export_labels=args.export_labels,
        )


if __name__ == "__main__":
    main()
