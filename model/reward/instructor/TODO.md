Some other reward features we can use

0. Finish classification feature

1. Summaries from human feedback

- use `confidence` score into the RM learning, ensure the output rank score
  correlates with confidence

- each labeling has a labeling `note`, basically comments by labeler, not sure
  what else we can use

- ~~Use the score for "overall", "accuracy", "coverage", "coherence" from
  axis/evals to train an addition model (rank additional aspect of the policy
  model)~~

  - this should be placed under experimental_dataset.py

2. Add support for anthropic dataset

- anthropic dataset is more like a conversation tree which is much complex than
  simply question-answer schema

  - this is basically a MCTS from alphazero.
