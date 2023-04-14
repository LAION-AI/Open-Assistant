from collections import defaultdict

import numpy as np
import pandas as pd
import psycopg2
from rankings import ranked_pairs
from scipy.stats import kendalltau


# source: wikipedia ;)
# but here without the normalization
def normalised_kendall_tau_distance(values1, values2):
    """Compute the Kendall tau distance."""
    n = len(values1)
    assert len(values2) == n, "Both lists have to be of equal length"
    i, j = np.meshgrid(np.arange(n), np.arange(n))
    a = np.argsort(values1)
    b = np.argsort(values2)
    ndisordered = np.logical_or(
        np.logical_and(a[i] < a[j], b[i] > b[j]), np.logical_and(a[i] > a[j], b[i] < b[j])
    ).sum()
    return ndisordered / (n * (n - 1))


def get_df():
    """
    Simple method that computes merged rankings and compares them to each user.
    Most interesting output for end-user is presumably the last that lists each user with their
    correlation to the mean ranking.
    Lower means less well aligned to the mean, higher means more well aligned.
    Note that rankings with fewer options are more likely to be wrong, so this could
    yield to misleading results:
    **You cannot use this for automatic flagging!**
    """
    conn = psycopg2.connect("host=0.0.0.0 port=5432 user=postgres password=postgres dbname=postgres")
    # Define the SQL query
    # query = """SELECT DISTINCT t.parent_message_id, r.user_id, r.payload->'payload'->>'ranked_message_ids' as ranked_ids
    #    FROM message_reaction r JOIN task t ON r.task_id = t.id
    #      WHERE r.payload->'payload'->>'type' = 'message_ranking';"""
    role = "'assistant'"
    message_tree_id = None  # "'ef458036-ae8e-4ff5-98f2-0f9dfedcb206'"
    query = f"""
        -- get all ranking results of completed tasks for all parents with >= 2 children
        SELECT DISTINCT p.parent_id, p.message_tree_id, mr.* FROM
        (
            -- find parents with > 1 children
            SELECT m.parent_id, m.message_tree_id, COUNT(m.id) children_count
            FROM message_tree_state mts
            INNER JOIN message m ON mts.message_tree_id = m.message_tree_id
            WHERE m.review_result                  -- must be reviewed
            AND NOT m.deleted                   -- not deleted
            AND m.parent_id IS NOT NULL         -- ignore initial prompts
            AND ({role} IS NULL OR m.role = {role}) -- children with matching role
            -- AND mts.message_tree_id = {message_tree_id}
            GROUP BY m.parent_id, m.message_tree_id
            HAVING COUNT(m.id) > 1
        ) as p
        LEFT JOIN task t ON p.parent_id = t.parent_message_id AND t.done AND (t.payload_type = 'RankPrompterRepliesPayload' OR t.payload_type = 'RankAssistantRepliesPayload')
        LEFT JOIN message_reaction mr ON mr.task_id = t.id AND mr.payload_type = 'RankingReactionPayload'
        """

    # Read the query results into a Pandas dataframe
    df = pd.read_sql(query, con=conn)
    print(df[["message_tree_id", "parent_id", "payload"]])
    # Close the database connection
    conn.close()
    users = set()
    messages = set()
    rankings = defaultdict(list)
    rankings_with_user = defaultdict(list)
    for row in df.itertuples(index=False):
        row = row._asdict()
        users.add(str(row["user_id"]))
        messages.add(str(row["message_tree_id"]))
        #
        if row["payload"] is None:
            continue
        ranking = row["payload"]["payload"]["ranked_message_ids"]
        rankings_with_user[str(row["parent_id"])].append((ranking, str(row["user_id"])))
        rankings[str(row["parent_id"])].append(ranking)
    print(*[f"{k} : {v}" for k, v in rankings.items()], sep="\n")
    users = list(users)
    messages = list(messages)
    consensus = dict()
    total_correlation = list()
    for k, v in rankings.items():
        # print("v",[len(i) for i in v])
        common_set = set.intersection(*map(set, v))
        # clean up the rankings and remove stuff not in all of them
        v = [list(filter(lambda x: x in common_set, ids)) for ids in v]
        merged_rankings = ranked_pairs(v)
        consensus[k] = merged_rankings
        ls = []
        for vote, id in rankings_with_user[k]:
            # clean up the rankings and remove stuff not in all of them
            vote = list(filter(lambda x: x in common_set, vote))
            ls.append((kendalltau(merged_rankings, vote), id))
        rankings_with_user[k] = ls
        total_correlation.extend(ls)
    correlation_by_user = defaultdict(list)
    for u in users:
        for c, m in total_correlation:
            if m == u:
                correlation_by_user[u].append(c)

    return consensus, users, messages, rankings_with_user, correlation_by_user


if __name__ == "__main__":
    cons, user, messages, rankings, correlation_by_user = get_df()
    # print(user)
    # print(messages)
    # print(rankings)
    # print("consensus:", cons)
    print("correlation_by_user:", correlation_by_user)
    for k, v in correlation_by_user.items():
        if len(v) < 50:
            res = "not enough data"
        else:
            i = list(map(lambda x: x, v))
            res = np.mean(i)
            res_std = np.std(i)
            print("result:", k, f" with value {res:.2f}", f"± {res_std:.2f}")
