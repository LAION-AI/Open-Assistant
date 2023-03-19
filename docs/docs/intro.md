# Introduction

> The FAQ page is available at
> [here](https://projects.laion.ai/Open-Assistant/docs/faq).

Open Assistant (abbreviated as OA) is a chat-based and open-source assistant.
The vision of the project is to make a large language model that can run on a
single high-end consumer GPU. With some modifications, Open Assistant should
also be able to interface with other third-party applications easily as well as
retrieve information from databases and the Internet.

You should join the
[Open Assistant discord server](https://ykilcher.com/open-assistant-discord)
and/or comment on Github issues before making any major changes. Most dev
communcations take place on the Discord server. There are four main areas that
you can work on:

1. Ranking, labelling and making responses in
   [open-assistant.io](https://www.open-assistant.io). You can take a look at
   [tasks docs section](https://projects.laion.ai/Open-Assistant/docs/tasks) for
   more information.
2. Curating datasets and performing data augmentation. This includes scraping,
   gathering other public datasets, etc. Most of these efforts will be
   concentrated at
   [`/data/datasets`](https://github.com/LAION-AI/Open-Assistant/tree/main/data/datasets)
   and are documented at
   [here](https://projects.laion.ai/Open-Assistant/docs/data/datasets).
3. Creating and fine-tuning Open Assistant itself. For that, you should pay
   special attention to
   [`/model`](https://github.com/LAION-AI/Open-Assistant/tree/main/model).
4. [open-assistant.io](https://www.open-assistant.io) dev. Take a close look at
   [`/website`](https://github.com/LAION-AI/Open-Assistant/tree/main/website) as
   well as
   [`/backend`](https://github.com/LAION-AI/Open-Assistant/tree/main/backend).

## GitHub folders explanation

> Do read the
> [developer guide](https://projects.laion.ai/Open-Assistant/docs/guides/developers)
> for further information.

Here's a list of first-level folders at
[Open Assistant's Github page](https://github.com/LAION-AI/Open-Assistant/).

- [`/ansible`](https://github.com/LAION-AI/Open-Assistant/tree/main/ansible) -
  for managing the full stack using
  [Ansible](<https://en.wikipedia.org/wiki/Ansible_(software)>)
- [`/assets`](https://github.com/LAION-AI/Open-Assistant/tree/main/assets) -
  contains logos
- [`/backend`](https://github.com/LAION-AI/Open-Assistant/tree/main/backend) -
  backend for open-assistant.io and discord bots, maybe helpful for locally test
  API calls
- [`/copilot`](https://github.com/LAION-AI/Open-Assistant/tree/main/copilot) -
  read more at AWS's [Copilot](https://aws.github.io/copilot-cli/). And no, this
  is not a folder that contains something similar to OpenAI's Codex.
- [`/data`](https://github.com/LAION-AI/Open-Assistant/tree/main/data) -
  contains
  [`/data/datasets`](https://github.com/LAION-AI/Open-Assistant/tree/main/data/datasets)
  that contains data scraping code and links to datasets on Hugging Face
- [`/deploy`](https://github.com/LAION-AI/Open-Assistant/tree/main/deploy)
- [`/discord-bot`](https://github.com/LAION-AI/Open-Assistant/tree/main/discord-bots) -
  frontend as discord bots for volunteer data collection
- [`/docker`](https://github.com/LAION-AI/Open-Assistant/tree/main/docker)
- [`/docs`](https://github.com/LAION-AI/Open-Assistant/tree/main/docs) - this
  website!
- [`/inference`](https://github.com/LAION-AI/Open-Assistant/tree/main/inference) -
  inference pipeline for Open Assistant model
- [`/model`](https://github.com/LAION-AI/Open-Assistant/tree/main/inference) -
  currently contains scripts and tools for training/fine-tuning Open Assistant
  and other neural networks
- [\*`/notebooks`](https://github.com/LAION-AI/Open-Assistant/tree/main/inference) -
  DEPRECATED in favor of\*
  [`/data/datasets`](https://github.com/LAION-AI/Open-Assistant/tree/main/data/datasets).
  Contains jupyter notebooks for data scraping and augmentation
- [`/oasst-shared`](https://github.com/LAION-AI/Open-Assistant/tree/main/oasst-shared) -
  shared Python code for Open Assistant
- [`/scripts`](https://github.com/LAION-AI/Open-Assistant/tree/main/scripts) -
  contains various scripts for things
- [`/text-frontend`](https://github.com/LAION-AI/Open-Assistant/tree/main/text-frontend)
- [`/website`](https://github.com/LAION-AI/Open-Assistant/tree/main/website) -
  everything in [open-assistant.io](https://www.open-assistant.io), including
  gamification

## Principles

- We put the human in the center
- We need to get the MVP out fast, while we still have momentum
- We pull in one direction
- We are pragmatic
- We aim for models that can (or could, with some effort) be run on consumer
  hardware
- We rapidly validate our ML experiments on a small scale, before going to a
  supercluster
