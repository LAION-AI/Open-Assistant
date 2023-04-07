import argparse
from pathlib import Path
from typing import List, Optional
from uuid import UUID

import sqlalchemy as sa
from loguru import logger
from oasst_backend.database import engine
from oasst_backend.models import Message, MessageEmoji, MessageReaction, MessageTreeState, TextLabels, db_payload
from oasst_backend.models.message_tree_state import State as TreeState
from oasst_backend.utils import tree_export
from oasst_data import (
    ExportMessageEvent,
    ExportMessageEventEmoji,
    ExportMessageEventRanking,
    ExportMessageEventRating,
    ExportMessageTree,
    LabelAvgValue,
    LabelValues,
)
from oasst_shared.schemas.protocol import TextLabel
from sqlmodel import Session, func


def fetch_tree_ids(
    db: Session,
    state_filter: Optional[TreeState] = None,
    lang: Optional[str] = None,
    synthetic: Optional[bool] = None,
    limit: Optional[int] = None,
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

    if synthetic is not None:
        synth_exists_qry = (
            db.query()
            .filter(Message.message_tree_id == MessageTreeState.message_tree_id, Message.synthetic)
            .exists()
            .correlate(MessageTreeState)
        )
        if synthetic is False:
            synth_exists_qry = ~synth_exists_qry
        tree_qry = tree_qry.filter(synth_exists_qry)

    if limit is not None:
        tree_qry = tree_qry.limit(limit)

    return [(tree.message_tree_id, tree.state) for tree in tree_qry]


def fetch_tree_messages(
    db: Session,
    message_tree_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    deleted: Optional[bool] = None,
    synthetic: Optional[bool] = False,
    prompts_only: bool = False,
    lang: Optional[str] = None,
    review_result: Optional[bool] = None,
    limit: Optional[int] = None,
) -> List[Message]:
    qry = db.query(Message)

    if message_tree_id:
        qry = qry.filter(Message.message_tree_id == message_tree_id)
    if user_id:
        qry = qry.filter(Message.user_id == user_id)
    if deleted is not None:
        qry = qry.filter(Message.deleted == deleted)
    if synthetic is not None:
        qry = qry.filter(Message.synthetic == synthetic)
    if prompts_only:
        qry = qry.filter(Message.parent_id.is_(None))
    if lang:
        qry = qry.filter(Message.lang == lang)
    if review_result is not None:
        qry = qry.filter(Message.review_result == review_result)
    if limit is not None:
        qry = qry.limit(limit)

    return qry.all()


def get_events_for_messages(db: Session, message_ids: list[UUID]) -> dict[UUID, ExportMessageEvent]:
    events = {}
    emojis = db.query(MessageEmoji).filter(MessageEmoji.message_id.in_(message_ids)).all()
    for emoji in emojis:
        event = ExportMessageEventEmoji(user_id=str(emoji.user_id), emoji=emoji.emoji)
        events.setdefault(emoji.message_id, {}).setdefault("emoji", []).append(event)
    reactions: list[MessageReaction] = (
        db.query(MessageReaction).filter(MessageReaction.message_id.in_(message_ids)).all()
    )
    for reaction in reactions:
        match reaction.payload_type:
            case "RatingReactionPayload":
                key = "rating"
                payload: db_payload.RatingReactionPayload = reaction.payload.payload
                event = ExportMessageEventRating(user_id=str(reaction.user_id), rating=payload.rating)
            case "RankingReactionPayload":
                key = "ranking"
                payload: db_payload.RankingReactionPayload = reaction.payload.payload
                event = ExportMessageEventRanking(
                    user_id=str(reaction.user_id),
                    ranking=payload.ranking,
                    ranked_message_ids=[str(id) for id in payload.ranked_message_ids],
                    ranking_parent_id=str(payload.ranking_parent_id) if payload.ranking_parent_id else None,
                    message_tree_id=str(payload.message_tree_id) if payload.message_tree_id else None,
                    not_rankable=payload.not_rankable if payload.not_rankable else None,
                )
            case _:
                raise ValueError(f"Unknown payload type {reaction.payload_type}")
        events.setdefault(reaction.message_id, {}).setdefault(key, []).append(event)

    return events


def fetch_tree_messages_and_avg_labels(
    db: Session,
    message_tree_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    deleted: Optional[bool] = None,
    synthetic: Optional[bool] = False,
    prompts_only: bool = False,
    lang: Optional[str] = None,
    review_result: Optional[bool] = None,
    limit: Optional[int] = None,
) -> List[Message]:
    args = [Message]

    for l in TextLabel:
        args.append(func.avg(TextLabels.labels[l].cast(sa.Float)).label(l.value))
        args.append(func.count(TextLabels.labels[l]).label(l.value + "_count"))

    qry = db.query(*args).select_from(Message).outerjoin(TextLabels, Message.id == TextLabels.message_id)
    if message_tree_id:
        qry = qry.filter(Message.message_tree_id == message_tree_id)
    if user_id:
        qry = qry.filter(Message.user_id == user_id)
    if deleted is not None:
        qry = qry.filter(Message.deleted == deleted)
    if synthetic is not None:
        qry = qry.filter(Message.synthetic == synthetic)
    if prompts_only:
        qry = qry.filter(Message.parent_id.is_(None))
    if lang:
        qry = qry.filter(Message.lang == lang)
    if review_result is not None:
        qry = qry.filter(Message.review_result == review_result)

    qry = qry.group_by(Message.id)

    if limit is not None:
        qry = qry.limit(limit)

    return qry.all()


def export_trees(
    db: Session,
    export_file: Optional[Path] = None,
    use_compression: bool = False,
    deleted: Optional[bool] = False,
    synthetic: Optional[bool] = False,
    user_id: Optional[UUID] = None,
    prompts_only: bool = False,
    state_filter: Optional[TreeState] = None,
    lang: Optional[str] = None,
    review_result: Optional[bool] = None,
    export_labels: bool = False,
    export_events: bool = False,
    limit: Optional[int] = None,
    anonymizer_seed: Optional[str] = None,
) -> None:
    message_labels: dict[UUID, LabelValues] = {}
    anonymizer = tree_export.Anonymizer(anonymizer_seed) if anonymizer_seed else None
    if user_id:
        # when filtering by user we don't have complete message trees, export as list
        result = fetch_tree_messages_and_avg_labels(
            db,
            user_id=user_id,
            deleted=deleted,
            synthetic=synthetic,
            prompts_only=prompts_only,
            lang=lang,
            review_result=review_result,
            limit=limit,
        )

        messages: list[Message] = []
        for r in result:
            msg = r["Message"]
            messages.append(msg)
            if export_labels:
                labels: LabelValues = {
                    l.value: LabelAvgValue(value=r[l.value], count=r[l.value + "_count"])
                    for l in TextLabel
                    if r[l.value] is not None
                }
                message_labels[msg.id] = labels

        events = {}
        if export_events:
            events = get_events_for_messages(db, [msg.id for msg in messages])

        tree_export.write_messages_to_file(
            export_file,
            messages,
            use_compression,
            labels=message_labels,
            anonymizer=anonymizer,
            events=events,
        )
    else:
        # tree export mode
        message_tree_ids = fetch_tree_ids(db, state_filter, lang=lang, limit=limit, synthetic=synthetic)

        message_trees: list[list[Message]] = []

        for tree_id, _ in message_tree_ids:
            if export_labels:
                result = fetch_tree_messages_and_avg_labels(
                    db,
                    message_tree_id=tree_id,
                    deleted=deleted,
                    synthetic=None,  # pass None here (export trees, filtering happend in fetch_tree_ids)
                    prompts_only=prompts_only,
                    lang=None,  # pass None, trees were selected based on lang of prompt
                    review_result=review_result,
                )

                messages: list[Message] = []
                for r in result:
                    msg = r["Message"]
                    messages.append(msg)
                    labels: LabelValues = {
                        l.value: LabelAvgValue(value=r[l.value], count=r[l.value + "_count"])
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
                    synthetic=None,  # pass None here (export trees, filtering happend in fetch_tree_ids)
                    prompts_only=prompts_only,
                    lang=None,  # pass None here, trees were selected based on lang of prompt
                    review_result=review_result,
                )
                message_trees.append(messages)

        if review_result is False or deleted is True or synthetic is True:
            # when exporting filtered we don't have complete message trees, export as list
            messages = [m for t in message_trees for m in t]  # flatten message list
            events = {}
            if export_events:
                events = get_events_for_messages(db, [msg.id for msg in messages])
            tree_export.write_messages_to_file(
                export_file,
                messages,
                use_compression,
                labels=message_labels,
                anonymizer=anonymizer,
                events=events,
            )
        else:
            trees_to_export: List[ExportMessageTree] = []

            for (message_tree_id, message_tree_state), message_tree in zip(message_tree_ids, message_trees):
                if len(message_tree) > 0:
                    events = {}
                    if export_events:
                        events = get_events_for_messages(db, [msg.id for msg in message_tree])
                    try:
                        t = tree_export.build_export_tree(
                            message_tree_id=message_tree_id,
                            message_tree_state=message_tree_state,
                            messages=message_tree,
                            labels=message_labels,
                            anonymizer=anonymizer,
                            events=events,
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
        help="Export including messages with no review or negative review result.",
    )
    parser.add_argument(
        "--spam-only",
        action="store_true",
        help="Export only messages with negative review result (implies --include-spam).",
    )
    parser.add_argument(
        "--include-synthetic",
        action="store_true",
        help="Include synthetic messages in export",
    )
    parser.add_argument(
        "--synthetic-only",
        action="store_true",
        help="Export only synthetic messages (implies --include-synth)",
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
    parser.add_argument(
        "--export-events",
        action="store_true",
        help="Include events for messages",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of trees to export. Leave at `None` to export all trees.",
    )
    parser.add_argument(
        "--anonymizer-seed",
        type=int,
        help="Seed for the anonymizer. If not specified, no anonymization will be performed.",
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

    synthetic: Optional[bool] = False
    if args.include_synthetic:
        synthetic = None
    if args.synthetic_only:
        synthetic = True

    if args.anonymizer_seed is None:
        logger.warning("No anonymizer seed provided, no anonymization will be performed.")

    with Session(engine) as db:
        export_trees(
            db,
            Path(args.export_file) if args.export_file is not None else None,
            use_compression=args.use_compression,
            deleted=deleted,
            synthetic=synthetic,
            user_id=UUID(args.user) if args.user is not None else None,
            prompts_only=args.prompts_only,
            state_filter=state_filter,
            lang=args.lang,
            review_result=review_result,
            export_labels=args.export_labels,
            export_events=args.export_events,
            limit=args.limit,
            anonymizer_seed=args.anonymizer_seed,
        )


if __name__ == "__main__":
    main()
