from typing import List

import numpy as np


def head_to_head_votes(ranks: List[List[int]]):
    tallies = np.zeros((len(ranks[0]), len(ranks[0])))
    names = sorted(ranks[0])
    ranks = np.array(ranks)
    # we want the sorted indices
    ranks = np.argsort(ranks, axis=1)
    for i in range(ranks.shape[1]):
        for j in range(i + 1, ranks.shape[1]):
            # now count the cases someone voted for i over j
            over_j = np.sum(ranks[:, i] < ranks[:, j])
            over_i = np.sum(ranks[:, j] < ranks[:, i])
            tallies[i, j] = over_j
            # tallies[i,j] = over_i
            tallies[j, i] = over_i
            # tallies[j,i] = over_j
    return tallies, names


def cycle_detect(pairs):
    """Recursively detect cylces by removing condorcet losers until either only one pair is left or condorcet loosers no longer exist
    This method upholds the invariant that in a ranking for all a,b either a>b or b>a for all a,b.


    Returns
    -------
    out : False if the pairs do not contain a cycle, True if the pairs contain a cycle


    """
    # get all condorcet losers (pairs that loose to all other pairs)
    # idea: filter all losers that are never winners
    # print("pairs", pairs)
    if len(pairs) <= 1:
        return False
    losers = [c_lose for c_lose in np.unique(pairs[:, 1]) if c_lose not in pairs[:, 0]]
    if len(losers) == 0:
        # if we recursively removed pairs, and at some point we did not have
        # a condorcet loser, that means everything is both a winner and loser,
        # yielding at least one (winner,loser), (loser,winner) pair
        return True

    new = []
    for p in pairs:
        if p[1] not in losers:
            new.append(p)
    return cycle_detect(np.array(new))


def get_winner(pairs):
    """
    This returns _one_ concordant winner.
    It could be that there are multiple concordant winners, but in our case
    since we are interested in a ranking, we have to choose one at random.
    """
    losers = np.unique(pairs[:, 1]).astype(int)
    winners = np.unique(pairs[:, 0]).astype(int)
    for w in winners:
        if w not in losers:
            return w


def get_ranking(pairs):
    """
    Abuses concordance property to get a (not necessarily unique) ranking.
    The lack of uniqueness is due to the potential existence of multiple
    equally ranked winners. We have to pick one, which is where
    the non-uniqueness comes from
    """
    if len(pairs) == 1:
        return list(pairs[0])
    w = get_winner(pairs)
    # now remove the winner from the list of pairs
    p_new = np.array([(a, b) for a, b in pairs if a != w])
    return [w] + get_ranking(p_new)


def ranked_pairs(ranks: List[List[int]]):
    """
    Expects a list of rankings for an item like:
        [("w","x","z","y") for _ in range(3)]
        + [("w","y","x","z") for _ in range(2)]
        + [("x","y","z","w") for _ in range(4)]
        + [("x","z","w","y") for _ in range(5)]
        + [("y","w","x","z") for _ in range(1)]
    This code is quite brain melting, but the idea is the following:
    1. create a head-to-head matrix that tallies up all win-lose combinations of preferences
    2. take all combinations that win more than they loose and sort those by how often they win
    3. use that to create an (implicit) directed graph
    4. recursively extract nodes from the graph that do not have incoming edges
    5. said recursive list is the ranking
    """
    tallies, names = head_to_head_votes(ranks)
    tallies = tallies - tallies.T
    # note: the resulting tally matrix should be skew-symmetric
    # order by strength of victory (using tideman's original method, don't think it would make a difference for us)
    sorted_majorities = []
    for i in range(len(ranks[0])):
        for j in range(len(ranks[0])):
            # you can never prefer yourself over yourself
            # we also have to pick one of the two choices,
            # if the preference is exactly zero...
            if tallies[i, j] >= 0 and i != j:
                sorted_majorities.append((i, j, tallies[i, j]))
    # we don't explicitly deal with tied majorities here
    sorted_majorities = np.array(sorted(sorted_majorities, key=lambda x: x[2], reverse=True))
    # now do lock ins
    lock_ins = []
    for x, y, _ in sorted_majorities:
        # invariant: lock_ins has no cycles here
        lock_ins.append((x, y))
        # print("lock ins are now",np.array(lock_ins))
        if cycle_detect(np.array(lock_ins)):
            # print("backup: cycle detected")
            # if there's a cycle, delete the new addition and continue
            lock_ins = lock_ins[:-1]
    # now simply return all winners in order, and attach the losers
    # to the back. This is because the overall loser might not be unique
    # and (by concordance property) may never exist in any winning set to begin with.
    # (otherwise he would either not be the loser, or cycles exist!)
    # Since there could be multiple overall losers, we just return them in any order
    # as we are unable to find a closer ranking
    numerical_ranks = np.array(get_ranking(np.array(lock_ins))).astype(int)
    conversion = [names[n] for n in numerical_ranks]
    return conversion


if __name__ == "__main__":
    ranks = """ (
        [("w", "x", "z", "y") for _ in range(1)]
        + [("w", "y", "x", "z") for _ in range(2)]
        # + [("x","y","z","w") for _ in range(4)]
        + [("x", "z", "w", "y") for _ in range(5)]
        + [("y", "w", "x", "z") for _ in range(1)]
        # [("y","z","w","x") for _ in range(1000)]
    )"""
    ranks = [
        [
            ("c5181083-d3e9-41e7-a935-83fb9fa01488"),
            ("dcf3d179-0f34-4c15-ae21-b8feb15e422d"),
            ("d11705af-5575-43e5-b22e-08d155fbaa62"),
        ],
        [
            ("d11705af-5575-43e5-b22e-08d155fbaa62"),
            ("c5181083-d3e9-41e7-a935-83fb9fa01488"),
            ("dcf3d179-0f34-4c15-ae21-b8feb15e422d"),
        ],
        [
            ("dcf3d179-0f34-4c15-ae21-b8feb15e422d"),
            ("c5181083-d3e9-41e7-a935-83fb9fa01488"),
            ("d11705af-5575-43e5-b22e-08d155fbaa62"),
        ],
        [
            ("d11705af-5575-43e5-b22e-08d155fbaa62"),
            ("c5181083-d3e9-41e7-a935-83fb9fa01488"),
            ("dcf3d179-0f34-4c15-ae21-b8feb15e422d"),
        ],
    ]
    rp = ranked_pairs(ranks)
    print(rp)
