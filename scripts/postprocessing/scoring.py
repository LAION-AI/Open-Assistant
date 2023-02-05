from dataclasses import dataclass, replace
from typing import Any

import numpy as np
import numpy.typing as npt
from scipy.stats import kendalltau


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
    num_prompts: int
    num_good_prompts: int
    num_rankings: int
    num_good_rankings: int

    #####################
    voting_points: int
    prompt_points: int
    ranking_points: int

    def voter_quality(self):
        return self.num_good_votes / self.num_votes

    def rank_quality(self):
        return self.num_good_rankings / self.num_rankings

    def prompt_quality(self):
        return self.num_good_prompts / self.num_prompts

    def is_well_behaved(self, threshhold_vote, threshhold_prompt, threshhold_rank):
        return (
            self.voter_quality() > threshhold_vote
            and self.prompt_quality() > threshhold_prompt
            and self.rank_quality() > threshhold_rank
        )

    def total_points(self, voting_weight, prompt_weight, ranking_weight):
        return (
            voting_weight * self.voting_points
            + prompt_weight * self.prompt_points
            + ranking_weight * self.ranking_points
        )


def score_update_votes(new_vote: int, consensus: npt.ArrayLike, voter_data: Voter) -> Voter:
    """
    This function returns the new "quality score" and points for a voter,
    after that voter cast a vote on a question.

    This function is only to be run when archiving a question
    i.e. the question has had sufficiently many votes, or we can't get more than "K" bits of information

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
    new_points = consensus_ranking[new_vote] + voter_data.voting_points

    # we need to correct for 0 indexing, if you are closer to "right" than "wrong" of the conensus,
    # it's a good vote
    new_good_votes = int(consensus_ranking[new_vote] > (len(consensus) - 1) / 2) + voter_data.num_good_votes
    new_num_votes = voter_data.num_votes + 1
    return replace(voter_data, num_votes=new_num_votes, num_good_votes=new_good_votes, voting_points=new_points)


def score_update_prompts(consensus: npt.ArrayLike, voter_data: Voter) -> Voter:
    """
    This function returns the gain of points for a given prompt's votes

    In contrast to the other score updating functions, we can run this online as new votes come in.
    i.e. the question has had sufficiently many votes, or we can't get more than "K" bits of information.


    Parameters:
            consensus (ArrayLike): all votes cast for this question
            voter_data (Voter): a "Voter" object that represents the person that wrote the prompt

        Returns:
            updated_voter (Voter): the new "quality score" and points for the voter
    """
    # produces the ranking of votes, e.g. for [100,300,200] it returns [0, 2, 1],
    # since 100 is the lowest, 300 the highest and 200 the middle value
    consensus_ranking = np.arange(len(consensus)) - len(consensus) // 2 + 1
    # expected consenus ranking (i.e. normalize the votes and multiply-sum with weightings)
    delta_votes = np.sum(consensus_ranking * consensus / sum(consensus))
    new_points = delta_votes + voter_data.prompt_points

    # we need to correct for 0 indexing, if you are closer to "right" than "wrong" of the conensus,
    # it's a good vote
    new_good_prompts = int(delta_votes > 0) + voter_data.num_good_prompts
    new_num_prompts = voter_data.num_prompts + 1
    return replace(
        voter_data,
        num_prompts=new_num_prompts,
        num_good_prompts=new_good_prompts,
        prompt_points=new_points,
    )


def score_update_ranking(user_ranking: npt.ArrayLike, consensus_ranking: npt.ArrayLike, voter_data: Voter) -> Voter:
    """
    This function returns the gain of points for a given ranking's votes

    This function is only to be run when archiving a question
    i.e. the question has had sufficiently many votes, or we can't get more than "K" bits of information

    we use the bubble-sort distance (or "kendall-tau" distance) to compare the two rankings
    we use this over spearman correlation since:
        "[Kendall's τ] approaches a normal distribution more rapidly than ρ, as N, the sample size, increases;
            and τ is also more tractable mathematically, particularly when ties are present"
    Gilpin, A. R. (1993). Table for conversion of Kendall's Tau to Spearman's
     Rho within the context measures of magnitude of effect for meta-analysis

    Further in
        "research design and statistical analyses, second edition, 2003"
    the authors note that at least from an significance test POV they will yield the same p-values

        Parameters:
            user_ranking (ArrayLike): ranking produced by the user
            consensus (ArrayLike): ranking produced after running the voting algorithm to merge into the consensus ranking
            voter_data (Voter): a "Voter" object that represents the person that wrote the prompt

        Returns:
            updated_voter (Voter): the new "quality score" and points for the voter
    """
    bubble_sort_distance, p_value = kendalltau(user_ranking, consensus_ranking)
    # normalize kendall-tau from [-1,1] into [0,1] range
    bubble_sort_distance = (1 + bubble_sort_distance) / 2
    new_points = bubble_sort_distance + voter_data.ranking_points
    new_good_rankings = int(bubble_sort_distance > 0.5) + voter_data.num_good_rankings
    new_num_rankings = voter_data.num_rankings + 1
    return replace(
        voter_data,
        num_rankings=new_num_rankings,
        num_good_rankings=new_good_rankings,
        ranking_points=new_points,
    )


if __name__ == "__main__":
    demo_voter = Voter(
        "abc",
        num_votes=10,
        num_good_votes=2,
        num_prompts=10,
        num_good_prompts=2,
        num_rankings=10,
        num_good_rankings=2,
        voting_points=6,
        prompt_points=0,
        ranking_points=0,
    )
    new_vote = 3
    consensus = np.array([200, 300, 100, 500])
    print(demo_voter)
    print("best   vote  ", score_update_votes(new_vote, consensus, demo_voter))
    new_vote = 2
    print("worst  vote  ", score_update_votes(new_vote, consensus, demo_voter))
    new_vote = 1
    print("medium vote  ", score_update_votes(new_vote, consensus, demo_voter))
    print("prompt writer", score_update_prompts(consensus, demo_voter))
    print("best   rank  ", score_update_ranking(np.array([0, 2, 1]), np.array([0, 2, 1]), demo_voter))
    print("medium rank  ", score_update_ranking(np.array([2, 0, 1]), np.array([0, 2, 1]), demo_voter))
    print("worst  rank  ", score_update_ranking(np.array([1, 0, 2]), np.array([0, 2, 1]), demo_voter))
