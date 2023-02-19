# I’m in! Now what?

[Join the OpenAssistant Contributors Discord Server!](https://ykilcher.com/open-assistant-discord),
this is for work coordination.

[Join the LAION Discord Server!](https://discord.com/invite/mVcgxMPD7e), it has
a dedicated channel and is more public.

[and / or the YK Discord Server](https://ykilcher.com/discord), also has a
dedicated, but not as active, channel.

[Visit the Notion](https://ykilcher.com/open-assistant)

### Taking on Tasks

We have a growing task list of
[issues](https://github.com/LAION-AI/Open-Assistant/issues). Find an issue that
appeals to you and make a comment that you'd like to work on it. Include in your
comment a brief description of how you'll solve the problem and if there are any
open questions you want to discuss. Once a project coordinator has assigned the
issue to you, start working on it.

If the issue is currently unclear but you are interested, please post in Discord
and someone can help clarify the issue in more detail.

**Always Welcome:** Documentation markdowns in `docs/`, docstrings, diagrams of
the system architecture, and other documentation.

### Submitting Work

We're all working on different parts of Open Assistant together. To make
contributions smoothly we recommend the following:

1.  [Fork this project repository](https://docs.github.com/en/get-started/quickstart/fork-a-repo)
    and clone it to your local machine. (Read more
    [About Forks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/about-forks))
1.  Before working on any changes, try to
    [sync the forked repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork)
    to keep it up-to-date with the upstream repository.
1.  On a
    [new branch](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-and-deleting-branches-within-your-repository)
    in your fork (aka a "feature branch" and not `main`) work on a small focused
    change that only touches on a few files.
1.  Run `pre-commit` and make sure all files have formatting fixed. This
    simplifies life for reviewers.
1.  Package up a small bit of work that solves part of the problem
    [into a Pull Request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork)
    and
    [send it out for review](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/requesting-a-pull-request-review).
    [Here](https://github.com/LAION-AI/Open-Assistant/pull/658) is an example PR
    for this project to illustrate this flow.
1.  If you're lucky, we can merge your change into `main` without any problems.
    If there are changes to files you're working on, resolve them by:
    1.  First try to rebase as suggested
        [in these instructions](https://timwise.co.uk/2019/10/14/merge-vs-rebase/#should-you-rebase).
    1.  If rebasing feels too painful, merge as suggested
        [in these instructions](https://timwise.co.uk/2019/10/14/merge-vs-rebase/#should-you-merge).
1.  Once you've resolved conflicts (if any), finish the review and
    [squash and merge](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges#squash-and-merge-your-commits)
    your PR (when squashing try to clean up or update the individual commit
    messages to be one sensible single one).
1.  Merge in your change and move on to a new issue or the second step of your
    current issue.

Additionally, if someone is working on an issue that interests you, ask if they
need help on it or would like suggestions on how to approach the issue. If so,
share wildly. If they seem to have a good handle on it, let them work on their
solution until a challenge comes up.

#### Tips

- At any point you can compare your feature branch to the upstream/main of
  `LAION-AI/Open-Assistant` by using a URL like this:
  https://github.com/LAION-AI/Open-Assistant/compare/main...andrewm4894:Open-Assistant:my-example-feature-branch.
  Obviously just replace `andrewm4894` with your own GitHub user name and
  `my-example-feature-branch` with whatever you called the feature branch you
  are working on, so something like
  `https://github.com/LAION-AI/Open-Assistant/compare/main...<your_github_username>:Open-Assistant:<your_branch_name>`.
  This will show the changes that would appear in a PR, so you can check this to
  make sure only the files you have changed or added will be part of the PR.
- Try not to work on the `main` branch in your fork - ideally you can keep this
  as just an updated copy of `main` from `LAION-AI/Open-Assistant`.
- If your feature branch gets messed up, just update the `main` branch in your
  fork and create a fresh new clean "feature branch" where you can add your
  changes one by one in separate commits or all as a single commit.

### When does a review finish

A review finishes when all blocking comments are addressed and at least one
owning reviewer has approved the PR. Be sure to acknowledge any non-blocking
comments either by making the requested change, explaining why it's not being
addressed now, or filing an issue to handle it later.

## Developer Setup

Work is organized in the
[project board](https://github.com/orgs/LAION-AI/projects/3).

**Anything that is in the `Todo` column and not assigned, is up for grabs.
Meaning we'd be happy for anyone to do these tasks.**

If you want to work on something, assign yourself to it or write a comment that
you want to work on it and what you plan to do.

- To get started with development, if you want to work on the backend, have a
  look at `scripts/backend-development/README.md`.
- If you want to work on any frontend, have a look at
  `scripts/frontend-development/README.md` to make a backend available.

There is also a minimal implementation of a frontend in the `text-frontend`
folder.

We are using Python 3.10 for the backend.

Check out the
[High-Level Protocol Architecture](https://www.notion.so/High-Level-Protocol-Architecture-6f1fd3551da74213b560ead369f132dc)

### Website

The website is built using Next.js and is in the `website` folder.

### Pre-commit

We are using `pre-commit` to enforce code style and formatting.

Install `pre-commit` from [its website](https://pre-commit.com) and run
`pre-commit install` to install the pre-commit hooks.

In case you haven't done this, have already committed, and CI is failing, you
can run `pre-commit run --all-files` to run the pre-commit hooks on all files.

### Deployment

Upon making a release on GitHub, all docker images are automatically built and
pushed to ghcr.io. The docker images are tagged with the release version and the
`latest` tag. Further, the ansible playbook in `ansible/dev.yaml` is run to
automatically deploy the built release to the dev machine.

### Contribute a Dataset

See
[here](https://github.com/LAION-AI/Open-Assistant/blob/main/openassistant/datasets/README.md)
