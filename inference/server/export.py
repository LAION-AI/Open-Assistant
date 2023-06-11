"""Script to facilitate exporting chat data from the server database."""

import argparse
import asyncio
import contextlib
import datetime as dt
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, TextIO

import sqlalchemy
import sqlmodel
from fastapi.encoders import jsonable_encoder
from oasst_data import (
    ExportMessageEvent,
    ExportMessageEventReport,
    ExportMessageEventScore,
    ExportMessageNode,
    ExportMessageTree,
)
from oasst_inference_server import deps
from oasst_inference_server.database import AsyncSession
from oasst_inference_server.models import DbChat, DbMessage
from oasst_shared.utils import Anonymizer


# see https://stackoverflow.com/questions/17602878/how-to-handle-both-with-open-and-sys-stdout-nicely
@contextlib.contextmanager
def smart_open(filename: str = None) -> TextIO:
    if filename and filename != "-":
        fh = open(filename, "wt", encoding="UTF-8")
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


def maybe_anonymize(anonymizer: Anonymizer | None, collection: str, key: str) -> str:
    if anonymizer:
        return anonymizer.anonymize(collection, key)
    else:
        return key


def prepare_export_events(
    chat: DbChat,
    message: DbMessage,
    anonymizer: Anonymizer | None = None,
) -> dict[str, list[ExportMessageEvent]]:
    export_events: dict[str, list[ExportMessageEvent]] = {}

    if message.reports:
        export_events["report"] = [
            ExportMessageEventReport(
                user_id=maybe_anonymize(anonymizer, "user", str(chat.user_id)),
                report_type=str(db_report.report_type),
                reason=db_report.reason,
            )
            for db_report in message.reports
        ]

    if message.score:
        export_events["score"] = [
            ExportMessageEventScore(
                user_id=maybe_anonymize(anonymizer, "user", str(chat.user_id)),
                score=message.score,
            )
        ]

    return export_events


def prepare_export_message_tree(
    chat: DbChat,
    anonymizer: Anonymizer | None = None,
) -> ExportMessageTree:
    messages: list[DbMessage] = chat.messages

    # Exclude messages without content (e.g. work still in progress or aborted)
    export_messages: list[ExportMessageNode] = [
        prepare_export_message_node(chat, message, anonymizer=anonymizer) for message in messages if message.content
    ]

    messages_by_parent = defaultdict(list)
    for message in export_messages:
        messages_by_parent[message.parent_id].append(message)

    def assign_replies(node: ExportMessageNode) -> ExportMessageNode:
        node.replies = messages_by_parent[node.message_id]
        for child in node.replies:
            assign_replies(child)
        return node

    prompt = assign_replies(messages_by_parent[None][0])
    return ExportMessageTree(message_tree_id=str(chat.id), tree_state="not_applicable", prompt=prompt)


def prepare_export_message_node(
    chat: DbChat,
    message: DbMessage,
    anonymizer: Anonymizer | None = None,
) -> ExportMessageNode:
    if message.worker_config:
        model_name = message.worker_config.model_config.model_id
    else:
        model_name = None

    # Chat prompts are human-written, responses are synthetic
    synthetic = message.role == "assistant"

    events: dict[str, list[ExportMessageEvent]] = prepare_export_events(chat, message, anonymizer=anonymizer)

    message_id = maybe_anonymize(anonymizer, "message", message.id)
    parent_id = maybe_anonymize(anonymizer, "message", message.parent_id)
    user_id = maybe_anonymize(anonymizer, "user", chat.user_id)

    return ExportMessageNode(
        message_id=message_id,
        parent_id=parent_id,
        user_id=user_id,
        created_date=message.created_at,
        text=message.content,
        role=message.role,
        synthetic=synthetic,
        model_name=model_name,
        events=events,
    )


def write_messages_to_file(
    file: Path,
    chats: list[DbChat],
    use_compression: bool = True,
    write_trees: bool = True,
    anonymizer: Anonymizer | None = None,
) -> None:
    out_buff: TextIO

    if use_compression:
        if not file:
            raise RuntimeError("File name must be specified when using compression.")
        out_buff = gzip.open(file, "wt", encoding="UTF-8")
    else:
        out_buff = smart_open(file)

    with out_buff as f:
        for chat in chats:
            if write_trees:
                export_chat = prepare_export_message_tree(chat, anonymizer=anonymizer)
                file_data = jsonable_encoder(export_chat, exclude_none=True)
                json.dump(file_data, f)
                f.write("\n")
            else:
                # Exclude messages without content (e.g. work still in progress or aborted)
                for message in filter(lambda m: m.content, chat.messages):
                    export_message = prepare_export_message_node(chat, message, anonymizer=anonymizer)
                    file_data = jsonable_encoder(export_message, exclude_none=True)
                    json.dump(file_data, f)
                    f.write("\n")


async def fetch_eligible_chats(session_generator, filters: list[Any]) -> list[DbChat]:
    """Fetch chats which are not opted out of data collection and match the given filters."""
    session: AsyncSession
    filters.append(DbChat.allow_data_use)
    async with session_generator() as session:
        query = (
            sqlmodel.select(DbChat)
            .filter(*filters)
            .options(
                sqlalchemy.orm.joinedload("*"),
            )
        )
        chats: list[DbChat] = (await session.exec(query)).unique().all()
        return chats


def export_chats(
    session_generator,
    export_path: Path,
    filters: list[Any],
    use_compression: bool = True,
    write_trees: bool = True,
    anonymizer_seed: str | None = None,
) -> None:
    eligible_chats: list[DbChat] = asyncio.run(fetch_eligible_chats(session_generator, filters))
    anonymizer = Anonymizer(anonymizer_seed) if anonymizer_seed else None

    write_messages_to_file(
        export_path,
        eligible_chats,
        write_trees=write_trees,
        use_compression=use_compression,
        anonymizer=anonymizer,
    )


def parse_date(date_str: str) -> dt.date:
    return dt.datetime.strptime(date_str, "%Y-%m-%d").date()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--export-file",
        type=str,
        help="Name of file to export chats to. If not provided, output will be sent to STDOUT",
    )
    parser.add_argument(
        "--no-compression",
        action="store_true",
        help="Disable compression when writing to file.",
    )
    parser.add_argument(
        "--write-flat",
        action="store_true",
        help="Write chats as individual messages rather than trees.",
    )
    parser.add_argument(
        "--anonymizer-seed",
        type=int,
        help="Seed for the anonymizer. If not specified, no anonymization will be performed.",
    )
    parser.add_argument(
        "--from-date",
        type=parse_date,
        help="Only export chats created on or after this date. Format: YYYY-MM-DD",
    )
    parser.add_argument(
        "--to-date",
        type=parse_date,
        help="Only export chats created on or before this date. Format: YYYY-MM-DD",
    )
    parser.add_argument(
        "--user-id",
        type=str,
        help="Only export chats created by this user.",
    )
    parser.add_argument(
        "--chat-id",
        type=str,
        help="Only export this chat.",
    )
    parser.add_argument(
        "--scored",
        action="store_true",
        help="Only export chats with at least one assistant message with score != 0.",
    ),
    parser.add_argument(
        "--reported",
        action="store_true",
        help="Only export chats with at least one reported message.",
    )
    return parser.parse_args()


def create_filters(args: argparse.Namespace) -> list[Any]:
    filters = []

    if args.from_date:
        filters.append(DbChat.created_at >= args.from_date)
    if args.to_date:
        filters.append(DbChat.created_at <= args.to_date)
    if args.user_id:
        filters.append(DbChat.user_id == args.user_id)
    if args.chat_id:
        filters.append(DbChat.id == args.chat_id)
    if args.scored:
        filters.append(DbChat.messages.any((DbMessage.role == "assistant") & (DbMessage.score != 0)))
    if args.reported:
        filters.append(DbChat.messages.any(DbMessage.reports.any()))

    return filters


def main():
    args = parse_args()

    export_path = Path(args.export_file) if args.export_file else None
    filters = create_filters(args)

    export_chats(
        deps.manual_create_session,
        export_path,
        filters,
        use_compression=not args.no_compression,
        write_trees=not args.write_flat,
        anonymizer_seed=args.anonymizer_seed,
    )


if __name__ == "__main__":
    main()
