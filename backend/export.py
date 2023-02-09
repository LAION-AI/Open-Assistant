import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from loguru import logger
from oasst_backend.database import engine
from oasst_backend.models import Message, MessageTreeState, message_tree_state
from oasst_backend.utils import tree_export
from sqlmodel import Session, not_


def fetch_tree_ids(db: Session, ready_only: bool = False):
    tree_qry = db.query(MessageTreeState)

    if ready_only:
        tree_qry = tree_qry.filter(MessageTreeState.state == message_tree_state.State.READY_FOR_EXPORT)

    message_trees = tree_qry.all()

    message_tree_ids = [tree.message_tree_id for tree in message_trees]
    return message_tree_ids


def fetch_message_ids(
    db: Session,
    message_tree_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    include_deleted: bool = False,
    deleted_only: bool = False,
) -> List[Message]:
    qry = db.query(Message)

    if message_tree_id:
        qry = qry.filter(Message.message_tree_id == message_tree_id)
    if user_id:
        qry = qry.filter(Message.user_id == user_id)
    if not include_deleted:
        qry = qry.filter(not_(Message.deleted))
    if deleted_only:
        qry = qry.filter(Message.deleted)

    return qry.all()


def export_trees(
    db: Session,
    export_file: Optional[Path] = None,
    use_compression: bool = False,
    ready_only: bool = False,
    include_deleted: bool = False,
    deleted_only: bool = False,
    user_id: Optional[UUID] = None,
):
    trees_to_export: List[tree_export.ExportMessageTree] = []

    if user_id:
        messages = fetch_message_ids(db, user_id=user_id, include_deleted=include_deleted, deleted_only=deleted_only)
        message_tree_ids = [msg.message_tree_id for msg in messages]
    else:
        message_tree_ids = fetch_tree_ids(db, ready_only)

    message_trees = [
        fetch_message_ids(db, message_tree_id=tree_id, include_deleted=include_deleted, deleted_only=deleted_only)
        for tree_id in message_tree_ids
    ]

    for message_tree_id, message_tree in zip(message_tree_ids, message_trees):
        trees_to_export.append(tree_export.build_export_tree(message_tree_id, message_tree))

    if export_file:
        tree_export.write_trees_to_file(export_file, trees_to_export, use_compression)
    else:
        sys.stdout.write(json.dumps(jsonable_encoder(trees_to_export), indent=2))


def validate_args(args):
    if args.deleted_only:
        args.include_deleted = True

    args.use_compression = args.export_file is not None and ".gz" in args.export_file

    if args.ready_only and args.user_id is not None:
        raise ValueError("Cannot use --ready-only when specifying a user ID")

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
        "--ready-only",
        action="store_true",
        help="Only export trees which are ready for use",
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
        "--user",
        type=str,
        help="Only export trees involving the user with the specified ID. Incompatible with --ready-only.",
    )

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    validate_args(args)

    with Session(engine) as db:
        export_trees(
            db,
            Path(args.export_file) if args.export_file is not None else None,
            args.use_compression,
            args.ready_only,
            args.include_deleted,
            args.deleted_only,
            UUID(args.user) if args.user is not None else None,
        )


if __name__ == "__main__":
    main()
