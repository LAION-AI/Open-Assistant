from enum import Enum

import numpy as np
from scipy import optimize


class Task(Enum):
    RANKING = 0
    ANSWER = 1
    PROMPT = 2
    VOTE = 3


def task_selection(
    num_ranking_tasks: int, current_prompts: int, target_num_prompts: int, p: float, answers_per_prompt: int
) -> Task:
    """
    This computes which task to serve to the user.
    In general, this method aims to get rankable tasks out of the active pool ASAP.
    Before checking anything else, we first have a p% probability of running a ranking task.
    After that, we can dynamically determine which task to serve by balancing the number of active tasks.

        Parameters:
            num_ranking_tasks (int): number of prompts that are ready to do ranking (i.e. have "answers_per_prompt" many answers)
            current_prompts (int): how many prompts are currently in the active pool
            target_num_prompts (int): how many prompts _should_ be in the active pool
            p (float): probability to serve a ranking task, if one is available
            answers_per_prompt (int): number of answers we want to have per prompt
        Returns:
            task (Task): the task Enum that corresponds to one of the four tasks
    """
    if num_ranking_tasks > 0 and np.random.rand() < p:
        return Task.RANKING
    rate = 50 / (current_prompts * 2)
    prob_prompt_task = 0.5 + (target_num_prompts - current_prompts) * rate
    # Yes, I'm too lazy to solve this analytically...
    prob_unfinished_prompt = optimize.linprog(
        np.array([1, 1]), A_eq=np.array([[1, 1], [1, -answers_per_prompt]]), b_eq=np.array([1, 0]), bounds=(0, None)
    ).x[0]
    if np.random.rand() < prob_prompt_task:
        if np.random.rand() < prob_unfinished_prompt:
            return Task.ANSWER
        else:
            return Task.PROMPT
    else:
        return Task.VOTE


def next_answer_task(possible_prompts, answers_per_prompt):
    """
    If the `task_selection`method returns "answer", you can use this method to decide which
    prompt should get an answer next.
    The goal of this is to finish off the prompts that have almost enough answers collected already:
    I.e. if we want 5 answers, this is going to give preferential sampling to those prompts that already
    have 4/5 answers.
    This helps to not have too much close-to-finished prompts in the active set.

        Parameters:
            possible_prompts (dict[prompt_id, num_answers]): a dictionary containing all open prompts and the number of answers these prompts currently have.
            answers_per_prompt (int): number of answers we per prompt to target
        Returns:
            prompt_id (int): the prompt_id corresponding to the next prompt that should get a new answer
    """
    nums = list(set(possible_prompts.values()))
    p = np.array([max(x / answers_per_prompt, 1 / answers_per_prompt) for x in nums])
    idx = np.random.choice(nums, p=p / p.sum())
    sample = np.random.choice([k for k, v in possible_prompts.items() if v == idx])
    return sample


if __name__ == "__main__":
    x = task_selection(1, 500, 1000, 0.1, 5)
    print(x)
    y = next_answer_task({"this": 2, "is": 4, "a": 1, "test": 4}, 5)
    print(y)
