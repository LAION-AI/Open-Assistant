# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import oasst_backend.models.db_payload as db_payload
from loguru import logger
from oasst_backend.journal_writer import JournalWriter
from oasst_backend.models import ApiClient, User, Post, PostReaction, TextLabels, WorkPackage
from oasst_backend.models.payload_column_type import PayloadContainer
from oasst_shared.schemas import protocol as protocol_schema
from sqlmodel import Session


class PromptRepository:
    def __init__(self, db: Session, api_client: ApiClient, user: Optional[protocol_schema.User]):
        self.db = db
        self.api_client = api_client
        self.user = self.lookup_user(user)
        self.user_id = self.user.id if self.user else None
        self.journal = JournalWriter(db, api_client, self.user)

    def lookup_user(self, user: protocol_schema.User) -> User:
        if not user:
            return None
        user: User = (
            self.db.query(User)
            .filter(
                User.api_client_id == self.api_client.id,
                User.username == user.id,
                User.auth_method == user.auth_method,
            )
            .first()
        )
        if user is None:
            # user is unknown, create new record
            user = User(
                username=user.id,
                display_name=user.display_name,
                api_client_id=self.api_client.id,
                auth_method=user.auth_method,
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        elif user.display_name and user.display_name != user.display_name:
            # we found the user but the display name changed
            user.display_name = user.display_name
            self.db.add(user)
            self.db.commit()
        return user

    def validate_post_id(self, post_id: str) -> None:
        if not isinstance(post_id, str):
            raise TypeError(f"post_id must be string, not {type(post_id)}")
        if not post_id:
            raise ValueError("post_id must not be empty")

    def bind_frontend_post_id(self, task_id: UUID, post_id: str):
        self.validate_post_id(post_id)

        # find work package
        work_pack: WorkPackage = (
            self.db.query(WorkPackage)
            .filter(WorkPackage.id == task_id, WorkPackage.api_client_id == self.api_client.id)
            .first()
        )
        if work_pack is None:
            raise KeyError(f"WorkPackage for task {task_id} not found")
        if work_pack.expiry_date is not None and datetime.utcnow() > work_pack.expiry_date:
            raise RuntimeError("WorkPackage already expired.")

        # ToDo: check race-condition, transaction

        # check if task thread exits
        thread_root = (
            self.db.query(Post)
            .filter(
                Post.workpackage_id == work_pack.id,
                Post.frontend_post_id == post_id,
                Post.parent_id is None,
                Post.api_client_id == self.api_client.id,
            )
            .one_or_none()
        )
        if thread_root is None:
            thread_id = uuid4()
            thread_root = self.insert_post(
                post_id=thread_id,
                thread_id=thread_id,
                frontend_post_id=post_id,
                parent_id=None,
                role="system",
                workpackage_id=work_pack.id,
                payload=None,
                payload_type="bind",
            )
        return thread_root

    def fetch_post_by_frontend_post_id(self, frontend_post_id: str, fail_if_missing: bool = True) -> Post:
        self.validate_post_id(frontend_post_id)
        post: Post = (
            self.db.query(Post)
            .filter(Post.api_client_id == self.api_client.id, Post.frontend_post_id == frontend_post_id)
            .one_or_none()
        )
        if fail_if_missing and post is None:
            raise KeyError(f"Post with post_id {frontend_post_id} not found.")
        return post

    def fetch_workpackage_by_postid(self, post_id: str) -> WorkPackage:
        self.validate_post_id(post_id)
        post = self.fetch_post_by_frontend_post_id(post_id, fail_if_missing=True)
        work_pack = self.db.query(WorkPackage).filter(WorkPackage.id == post.workpackage_id).one()
        return work_pack

    def store_text_reply(self, reply: protocol_schema.TextReplyToPost, role: str) -> Post:
        self.validate_post_id(reply.post_id)
        self.validate_post_id(reply.user_post_id)

        work_package = self.fetch_workpackage_by_postid(reply.post_id)
        work_payload: db_payload.TaskPayload = work_package.payload.payload
        logger.info(f"found task work package in db: {work_payload}")

        # find post with post-id
        parent_post: Post = (
            self.db.query(Post)
            .filter(
                Post.api_client_id == self.api_client.id,
                Post.frontend_post_id == reply.post_id,
                # Post.user_id == self.user_id
            )
            .one_or_none()
        )

        if parent_post is None:
            raise KeyError(f"Post for post_id {reply.post_id} not found.")

        # create reply post
        user_post_id = uuid4()
        user_post = self.insert_post(
            post_id=user_post_id,
            frontend_post_id=reply.user_post_id,
            parent_id=parent_post.id,
            thread_id=parent_post.thread_id,
            workpackage_id=parent_post.workpackage_id,
            role=role,
            payload=db_payload.PostPayload(text=reply.text),
        )
        self.journal.log_text_reply(work_package=work_package, post_id=user_post_id, role=role, length=len(reply.text))
        return user_post

    def store_rating(self, rating: protocol_schema.PostRating) -> PostReaction:
        post = self.fetch_post_by_frontend_post_id(rating.post_id, fail_if_missing=True)

        work_package = self.fetch_workpackage_by_postid(rating.post_id)
        work_payload: db_payload.RateSummaryPayload = work_package.payload.payload
        if type(work_payload) != db_payload.RateSummaryPayload:
            raise ValueError(
                f"work_package payload type mismatch: {type(work_payload)=} != {db_payload.RateSummaryPayload}"
            )

        if rating.rating < work_payload.scale.min or rating.rating > work_payload.scale.max:
            raise ValueError(f"Invalid rating value: {rating.rating=} not in {work_payload.scale=}")

        # store reaction to post
        reaction_payload = db_payload.RatingReactionPayload(rating=rating.rating)
        reaction = self.insert_reaction(post.id, reaction_payload)
        self.journal.log_rating(work_package, post_id=post.id, rating=rating.rating)
        logger.info(f"Ranking {rating.rating} stored for work_package {work_package.id}.")
        return reaction

    def store_ranking(self, ranking: protocol_schema.PostRanking) -> PostReaction:
        post = self.fetch_post_by_frontend_post_id(ranking.post_id, fail_if_missing=True)

        # fetch work_package
        work_package = self.fetch_workpackage_by_postid(ranking.post_id)
        work_payload: db_payload.RankConversationRepliesPayload | db_payload.RankInitialPromptsPayload = (
            work_package.payload.payload
        )

        match type(work_payload):

            case db_payload.RankUserRepliesPayload | db_payload.RankAssistantRepliesPayload:
                # validate ranking
                num_replies = len(work_payload.replies)
                if sorted(ranking.ranking) != list(range(num_replies)):
                    raise ValueError(
                        f"Invalid ranking submitted. Each reply index must appear exactly once ({num_replies=})."
                    )

                # store reaction to post
                reaction_payload = db_payload.RankingReactionPayload(ranking=ranking.ranking)
                reaction = self.insert_reaction(post.id, reaction_payload)
                self.journal.log_ranking(work_package, post_id=post.id, ranking=ranking.ranking)

                logger.info(f"Ranking {ranking.ranking} stored for work_package {work_package.id}.")

                return reaction

            case db_payload.RankInitialPromptsPayload:
                # validate ranking
                if sorted(ranking.ranking) != list(range(num_prompts := len(work_payload.prompts))):
                    raise ValueError(
                        f"Invalid ranking submitted. Each reply index must appear exactly once ({num_prompts=})."
                    )

                # store reaction to post
                reaction_payload = db_payload.RankingReactionPayload(ranking=ranking.ranking)
                reaction = self.insert_reaction(post.id, reaction_payload)
                self.journal.log_ranking(work_package, post_id=post.id, ranking=ranking.ranking)

                logger.info(f"Ranking {ranking.ranking} stored for work_package {work_package.id}.")

                return reaction

            case _:
                raise ValueError(
                    f"work_package payload type mismatch: {type(work_payload)=} != {db_payload.RankConversationRepliesPayload}"
                )

    def store_task(self, task: protocol_schema.Task) -> WorkPackage:
        payload: db_payload.TaskPayload
        match type(task):
            case protocol_schema.SummarizeStoryTask:
                payload = db_payload.SummarizationStoryPayload(story=task.story)

            case protocol_schema.RateSummaryTask:
                payload = db_payload.RateSummaryPayload(
                    full_text=task.full_text, summary=task.summary, scale=task.scale
                )

            case protocol_schema.InitialPromptTask:
                payload = db_payload.InitialPromptPayload(hint=task.hint)

            case protocol_schema.UserReplyTask:
                payload = db_payload.UserReplyPayload(conversation=task.conversation, hint=task.hint)

            case protocol_schema.AssistantReplyTask:
                payload = db_payload.AssistantReplyPayload(type=task.type, conversation=task.conversation)

            case protocol_schema.RankInitialPromptsTask:
                payload = db_payload.RankInitialPromptsPayload(tpye=task.type, prompts=task.prompts)

            case protocol_schema.RankUserRepliesTask:
                payload = db_payload.RankUserRepliesPayload(
                    tpye=task.type, conversation=task.conversation, replies=task.replies
                )

            case protocol_schema.RankAssistantRepliesTask:
                payload = db_payload.RankAssistantRepliesPayload(
                    tpye=task.type, conversation=task.conversation, replies=task.replies
                )

            case _:
                raise ValueError(f"Invalid task type: {type(task)=}")

        wp = self.insert_work_package(payload=payload, id=task.id)
        assert wp.id == task.id
        return wp

    def insert_work_package(self, payload: db_payload.TaskPayload, id: UUID = None) -> WorkPackage:
        c = PayloadContainer(payload=payload)
        wp = WorkPackage(
            id=id,
            user_id=self.user_id,
            payload_type=type(payload).__name__,
            payload=c,
            api_client_id=self.api_client.id,
        )
        self.db.add(wp)
        self.db.commit()
        self.db.refresh(wp)
        return wp

    def insert_post(
        self,
        *,
        post_id: UUID,
        frontend_post_id: str,
        parent_id: UUID,
        thread_id: UUID,
        workpackage_id: UUID,
        role: str,
        payload: db_payload.PostPayload,
        payload_type: str = None,
    ) -> Post:
        if payload_type is None:
            if payload is None:
                payload_type = "null"
            else:
                payload_type = type(payload).__name__

        post = Post(
            id=post_id,
            parent_id=parent_id,
            thread_id=thread_id,
            workpackage_id=workpackage_id,
            user_id=self.user_id,
            role=role,
            frontend_post_id=frontend_post_id,
            api_client_id=self.api_client.id,
            payload_type=payload_type,
            payload=PayloadContainer(payload=payload),
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def insert_reaction(self, post_id: UUID, payload: db_payload.ReactionPayload) -> PostReaction:
        if self.user_id is None:
            raise ValueError("User required")

        container = PayloadContainer(payload=payload)
        reaction = PostReaction(
            post_id=post_id,
            user_id=self.user_id,
            payload=container,
            api_client_id=self.api_client.id,
            payload_type=type(payload).__name__,
        )
        self.db.add(reaction)
        self.db.commit()
        self.db.refresh(reaction)
        return reaction

    def store_text_labels(self, text_labels: protocol_schema.TextLabels) -> TextLabels:
        model = TextLabels(
            api_client_id=self.api_client.id,
            text=text_labels.text,
            labels=text_labels.labels,
        )
        if text_labels.has_post_id:
            self.fetch_post_by_frontend_post_id(text_labels.post_id, fail_if_missing=True)
            model.post_id = text_labels.post_id
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model
