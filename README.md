# Open-Assistant

Open Assistant is a project meant to give everyone access to a great chat based large language model.

We believe that by doing this we will create a revolution in innovation in language. In the same way that stable-diffusion helped the world make art and images in new ways we hope Open Assistant can help improve the world by improving language itself.

## The Plan

We want to get to an initial MVP as fast as possible, by following the 3-steps outlined in the InstructGPT paper.

1. Collect high-quality human generated Instruction-Fulfillment samples (prompt + response), goal >50k. We design a crowdsourced process to collect and reviewed prompts. We do not want to train on flooding/toxic/spam/junk/personal information data. We will have a leaderboard to motivate the community that shows progress and the most active users. Swag will be given to the top-contributors.
2. For each of the collected prompts we will sample multiple completions. Completions of one prompt will then be shown randomly to users to rank them from best to worst. Again this should happen crowd-sourced, e.g. we need to deal with unreliable potentially malicious users. At least multiple votes by independent users have to be collected to measure the overall agreement. The gathered ranking-data will be used to train a reward model.
3. Now follows the RLHF training phase based on the prompts and the reward model.

We can then take the resulting model and continue with completion sampling step 2 for a next iteration.

## The Vision

We are not going to stop at replicating ChatGPT. We want to build the assistant of the future, able to not only write email and cover letters, but do meaningful work, use APIs, dynamically research information, and much more, with the ability to be personalized and extended by anyone. And we want to do this in a way that is open and accessible, which means we must not only build a great assistant, but also make it small and efficient enough to run on consumer hardware.

## How can you help?

All open source projects begins with people like you. Open source is the belief that if we collaborate we can together gift our knowledge and technology to the world for the benefit of humanity.

## I’m in! Now what?

[Fill out the contributor signup form](https://docs.google.com/forms/d/e/1FAIpQLSeuggO7UdYkBvGLEJldDvxp6DwaRbW5p7dl96UzFkZgziRTrQ/viewform)

[Join the LAION Discord Server!](https://discord.com/invite/mVcgxMPD7e)

[Visit the Notion](https://ykilcher.com/open-assistant)

## Developer Setup

Work is organized in the [project board](https://github.com/orgs/LAION-AI/projects/3).

**Anything that is in the `Todo` column and not assigned, is up for grabs. Meaning we'd be happy if anyone did those tasks.**

If you want to work on something, assign yourself to it or write a comment that you want to work on it and what you plan to do.

- To get started with development, if you want to work on the backend, have a look at `scripts/backend-development/README.md`.
- If you want to work on any frontend, have a look at `scripts/frontend-development/README.md` to make a backend available.

There is also a minimal implementation of a frontend in the `text-frontend` folder.

We are using Python 3.10 for the backend.

Check out the [High-Level Protocol Architecture](https://www.notion.so/High-Level-Protocol-Architecture-6f1fd3551da74213b560ead369f132dc)

## End to End Demo

If you are interested in just taking a look at the project.
You can set up an entire stack needed to run Open Assistant, including the
website, backend, and associated dependent services.

To start the demo, run this, in root directory:

```sh
docker compose up --build
```

Then, navigate to `http://localhost:3000` and interact with the website. When
logging in, navigate to `http://localhost:1080` to get the magic email login
link.

### Website

The website is built using Next.js and is in the `website` folder.

### Pre-commit

Install `pre-commit` and run `pre-commit install` to install the pre-commit hooks.

In case you haven't done this, have already committed, and CI is failing, you can run `pre-commit run --all-files` to run the pre-commit hooks on all files.

### Deployment

Upon making a release on GitHub, all docker images are automatically built and pushed to ghcr.io. The docker images are tagged with the release version, and the `latest` tag. Further, the ansible playbook in `ansible/dev.yaml` is run to automatically deploy the built release to the dev machine.
