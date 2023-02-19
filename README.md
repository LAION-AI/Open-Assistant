<h1 align="center">
    <span>Open-Assistant</span>
  <img width="auto" height="50px" src="https://github.com/LAION-AI/Open-Assistant/blob/main/assets/logo_crop.png"/>
</h1>

<div align="center">

<a href="https://github.com/LAION-AI/Open-Assistant/stargazers">![GitHub Repo stars](https://img.shields.io/github/stars/LAION-AI/Open-Assistant?style=social)</a>
<a href="https://laion-ai.github.io/Open-Assistant/">![Docs](https://img.shields.io/badge/docs-laion--ai.github.io%2FOpen--Assistant%2F-green)</a>
<a href="https://github.com/LAION-AI/Open-Assistant/actions/workflows/build-frontend.yaml">![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/LAION-AI/Open-Assistant/build-frontend.yaml?label=frontend)</a>
<a href="https://github.com/LAION-AI/Open-Assistant/actions/workflows/pre-commit.yaml">![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/LAION-AI/Open-Assistant/pre-commit.yaml?label=pre-commit)</a>
<a href="https://github.com/LAION-AI/Open-Assistant/actions/workflows/test-api-contract.yaml">![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/LAION-AI/Open-Assistant/test-api-contract.yaml?label=api)</a>
<a href="https://github.com/LAION-AI/Open-Assistant/releases">![GitHub release (latest by date)](https://img.shields.io/github/v/release/LAION-AI/Open-Assistant)</a>

</div>

# Here is our website to collect data:

[open-assistant.io](https://open-assistant.io)

(project documentation lives [here](https://laion-ai.github.io/Open-Assistant/))

# Table of Contents

- [What is Open Assistant?](#what-is-open-assistant)
- [Do you want to try it out?](#do-you-want-to-try-it-out)
- [The Plan](#the-plan)
- [The Vision](#the-vision)
- [How can you help?](#how-can-you-help)
- [I’m in! How do I contribute?](CONTRIBUTING.md)

---

## What is Open Assistant?

<p align="center">
    Open Assistant is a project meant to give everyone access to a great chat based large language model.
</p>

We believe that by doing this we will create a revolution in innovation in
language. In the same way that stable-diffusion helped the world make art and
images in new ways we hope Open Assistant can help improve the world by
improving language itself.

## Do you want to try it out?

### Contributing to Data Collection

The data collection frontend is now live [here](https://open-assistant.io/). Log
in and start taking on tasks! We want to collect a high volume of quality data.
By submitting, ranking, and labelling model prompts and responses you will be
directly helping to improve the capabilities of Open Assistant.

### Running Locally

**You do not need to run the project locally unless you are contributing to the
development process. The website link above will take you to the public website
where you can use the data collection app.**

If you would like to run the data collection app locally for development, you
can set up an entire stack needed to run **Open-Assistant**, including the
website, backend, and associated dependent services, with Docker.

To start the demo, run this in the root directory of the repository (check
[this FAQ](https://projects.laion.ai/Open-Assistant/docs/faq#docker-compose-instead-of-docker-compose)
if you have problems):

```sh
docker compose --profile ci up --build --attach-dependencies
```

Then, navigate to `http://localhost:3000` (It may take some time to boot up) and
interact with the website.

> **Note:** If an issue occurs with the build, please head to the
> [FAQ](https://projects.laion.ai/Open-Assistant/docs/faq) and check out the
> entries about Docker.

> **Note:** When logging in via email, navigate to `http://localhost:1080` to
> get the magic email login link.

> **Note:** If you would like to run this in a standardized development
> environment (a
> ["devcontainer"](https://code.visualstudio.com/docs/devcontainers/containers))
> using
> [vscode locally](https://code.visualstudio.com/docs/devcontainers/create-dev-container#_create-a-devcontainerjson-file)
> or in a web browser using
> [GitHub Codespaces](https://github.com/features/codespaces), you can use the
> provided [`.devcontainer`](.devcontainer/) folder.

## The Plan

##### We want to get to an initial MVP as fast as possible, by following the 3-steps outlined in the [InstructGPT paper](https://arxiv.org/abs/2203.02155).

1. Collect high-quality human generated Instruction-Fulfillment samples
   (prompt + response), goal >50k. We design a crowdsourced process to collect
   and reviewed prompts. We do not want to train on
   flooding/toxic/spam/junk/personal information data. We will have a
   leaderboard to motivate the community that shows progress and the most active
   users. Swag will be given to the top-contributors.
2. For each of the collected prompts we will sample multiple completions.
   Completions of one prompt will then be shown randomly to users to rank them
   from best to worst. Again this should happen crowd-sourced, e.g. we need to
   deal with unreliable potentially malicious users. At least multiple votes by
   independent users have to be collected to measure the overall agreement. The
   gathered ranking-data will be used to train a reward model.
3. Now follows the RLHF training phase based on the prompts and the reward
   model.

We can then take the resulting model and continue with completion sampling step
2 for a next iteration.

## The Vision

We are not going to stop at replicating ChatGPT. We want to build the assistant
of the future, able to not only write email and cover letters, but do meaningful
work, use APIs, dynamically research information, and much more, with the
ability to be personalized and extended by anyone. And we want to do this in a
way that is open and accessible, which means we must not only build a great
assistant, but also make it small and efficient enough to run on consumer
hardware.

### Slide Decks

[Vision & Roadmap](https://docs.google.com/presentation/d/1n7IrAOVOqwdYgiYrXc8Sj0He8krn5MVZO_iLkCjTtu0/edit?usp=sharing)

[Important Data Structures](https://docs.google.com/presentation/d/1iaX_nxasVWlvPiSNs0cllR9L_1neZq0RJxd6MFEalUY/edit?usp=sharing)

## How can you help?

All open source projects begin with people like you. Open source is the belief
that if we collaborate we can together gift our knowledge and technology to the
world for the benefit of humanity.

Check out our [contributing guide](CONTRIBUTING.md) to get started.
