# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Any

import numpy as np
import numpy.typing as npt


@dataclass
class Voter:
    """
    Represents a single voter.
    This tabulates the number of good votes, total votes,
    and points.
    We only put well-behaved people on the scoreboard and filter out the badly behaved ones
    """

    uid: Any
    num_votes: int
    num_good_votes: int
    total_points: int

    def voter_quality(self):
        return self.num_good_votes / self.num_votes

    def is_well_behaved(self, threshhold):
        return self.voter_quality() > threshhold


def score_update(new_vote: int, consensus: npt.ArrayLike, voter_data: Voter) -> Voter:
    """
    This function returns the new "quality score" and points for a voter.
    I.e. a voter casts a vote on a question.
    The consensus is the array of all votes cast by all voters for that question
    We then update the voter data using the new information

        Parameters:
            new_vote (int): the index of the vote cast by the voter
            consensus (ArrayLike): all votes cast for this question
            voter_data (Voter): a "Voter" object that represents the person casting the "new_vote"

        Returns:
            updated_voter (Voter): the new "quality score" and points for the voter
    """
    # produces the ranking of votes, e.g. for [100,300,200] it returns [0, 2, 1],
    # since 100 is the lowest, 300 the highest and 200 the middle value
    consensus_ranking = np.argsort(np.argsort(consensus))
    new_points = consensus_ranking[new_vote] + voter_data.total_points
    # we need to correct for 0 indexing, if you are closer to "right" than "wrong" of the conensus,
    # it's a good vote
    new_good_votes = int(consensus_ranking[new_vote] > (len(consensus) - 1) / 2) + voter_data.num_good_votes
    new_num_votes = voter_data.num_votes + 1
    return Voter(voter_data.uid, new_num_votes, new_good_votes, new_points)


if __name__ == "__main__":
    demo_voter = Voter("abc", 10, 2, 6)
    new_vote = 3
    consensus = np.array([200, 300, 100, 500])
    print(demo_voter)
    print("best   vote", score_update(new_vote, consensus, demo_voter))
    new_vote = 2
    print("worst  vote", score_update(new_vote, consensus, demo_voter))
    new_vote = 1
    print("medium vote", score_update(new_vote, consensus, demo_voter))
