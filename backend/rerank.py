import argparse
from uuid import UUID

import oasst_backend.utils.database_utils as db_utils
from export import fetch_tree_ids
from loguru import logger
from oasst_backend.api.deps import create_api_client
from oasst_backend.database import engine
from oasst_backend.models.api_client import ApiClient
from oasst_backend.models.message_tree_state import State as TreeState
from oasst_backend.prompt_repository import PromptRepository
from oasst_backend.tree_manager import TreeManager
from sqlmodel import Session
from tqdm import tqdm

IMPORT_API_CLIENT_ID = UUID("bd8fde8b-1d8e-4e9a-9966-e96d000f8363")


def update_tree_ranking(tm: TreeManager, message_tree_id: UUID) -> int:
    ranking_role_filter = None if tm.cfg.rank_prompter_replies else "assistant"
    rankings_by_message = tm.query_tree_ranking_results(message_tree_id, role_filter=ranking_role_filter)
    if len(rankings_by_message) == 0:
        logger.warning(f"No ranking results found for message tree {message_tree_id}")
        return 0
    num_updated = 0
    for rankings in rankings_by_message.values():
        if len(rankings) > 0:
            num_updated += tm.ranked_pairs_update(rankings)
    return num_updated


def parse_args():
    parser = argparse.ArgumentParser(description="Update message ranks with feedback received after tree-completion.")
    parser.add_argument("--commit", action="store_true", default=False, help="Dry run with rollback if not specified")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    dry_run = not args.commit

    @db_utils.managed_tx_function(auto_commit=db_utils.CommitMode.ROLLBACK if dry_run else db_utils.CommitMode.COMMIT)
    def update_rankings_tx(db: Session, api_client: ApiClient, message_tree_id: UUID) -> int:
        # create tree manager
        tm = TreeManager(db, PromptRepository(db, api_client=api_client))
        return update_tree_ranking(tm, message_tree_id)

    with Session(engine) as db:
        # get api client
        api_client = db.query(ApiClient).filter(ApiClient.id == IMPORT_API_CLIENT_ID).first()
        if not api_client:
            api_client = create_api_client(
                session=db,
                description="API client used for importing data",
                frontend_type="import",
                force_id=IMPORT_API_CLIENT_ID,
            )

        # find all ready for export trees
        tree_ids = fetch_tree_ids(db, state_filter=TreeState.READY_FOR_EXPORT)
        num_updated = 0

        for message_tree_id, _ in tqdm(tree_ids):
            try:
                num_updated += update_rankings_tx(api_client=api_client, message_tree_id=message_tree_id)
            except Exception:
                logger.exception(f"Update ranking of message tree {message_tree_id} failed")

    logger.info(f"Rank of {num_updated} messages updated.")

    if dry_run:
        logger.info("DRY RUN with rollback (run with --commit to modify db)")


if __name__ == "__main__":
    main()
