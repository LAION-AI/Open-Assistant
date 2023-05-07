# Frequently Asked Questions

> This pages covers specific questions. A more general introduction to the
> project and its goals can be found
> [here](https://projects.laion.ai/Open-Assistant/docs/intro).

In this page, there are some of the most frequently asked questions.

## Questions about the project

<details>
<summary>

### How far along is this project?

</summary>

We have released candidate supervised finetuning (SFT) models using both Pythia
and LLaMa, as well as candidate reward models for reinforcement learning from
human feedback training using Pythia, which you can try, and are beginning the
process of applying (RLHF). We have also released the first version of the
OpenAssistant Conversations dataset
[here](https://huggingface.co/datasets/OpenAssistant/oasst1).

</details>

<details>
<summary>

### Is a model ready to test yet?

</summary>

You can play with our best candidate model
[here](https://open-assistant.io/chat) and provide thumbs up/down responses to
help us improve the model in future!

</details>

<details>
<summary>

### Can I install Open Assistant locally and chat with it?

</summary>

The candidate Pythia SFT models are
[available on HuggingFace](https://huggingface.co/OpenAssistant) and can be
loaded via the HuggingFace Transformers library. As such you may be able to use
them with sufficient hardware. There are also spaces on HF which can be used to
chat with the OA candidate without your own hardware. However, these models are
not final and can produce poor or undesirable outputs.

LLaMa SFT models cannot be released directly due to Meta's license but XOR
weights are released on the HuggingFace org. Follow the process in the README
there to obtain a full model from these XOR weights.

</details>

<details>
<summary>

### Is there an API available?

</summary>

There is no API currently available for Open Assistant. Any mention of an API in
documentation is referencing the website's internal API. We understand that an
API is a highly requested feature, but unfortunately, we can't provide one at
this time due to a couple of reasons. Firstly, the inference system is already
under high load and running off of compute from our sponsors. Secondly, the
project's primary goal is currently data collection and model training, not
providing a product.

However, if you're looking to run inference, you can host the model yourself
either on your own hardware or with a cloud provider. We appreciate your
understanding and patience as we continue to develop this project.

</details>

<details>
<summary>

### What is the Docker command in the README for?

</summary>

The `docker compose` command in the README is for setting up the project for
local development on the website or data collection backend. It does not launch
an AI model or the inference server. There is likely no point in running the
inference setup and UI locally unless you wish to assist in development.

</details>

<details>
<summary>

### What license does Open Assistant use?

</summary>

All Open Assistant code is licensed under Apache 2.0. This means it is available
for a wide range of uses including commercial use.

The Open Assistant Pythia based models are released as full weights and will be
licensed under the Apache 2.0 license.

The Open Assistant LLaMa based models will be released only as delta weights
meaning you will need the original LLaMa weights to use them, and the license
restrictions will therefore be those placed on the LLaMa weights.

The Open Assistant data is released under a Creative Commons license allowing a
wide range of uses including commercial use.

</details>

<details>
<summary>

### Who is behind Open Assistant?

</summary>

Open Assistant is a project organized by [LAION](https://laion.ai/) and
developed by a team of volunteers worldwide. You can see an incomplete list of
developers on [our website](https://open-assistant.io/team).

The project would not be possible without the many volunteers who have spent
time contributing both to data collection and to the development process. Thank
you to everyone who has taken part!

</details>

<details>
<summary>

### Will Open Assistant be free?

</summary>

The model code, weights, and data are free. We are additionally hosting a free
public instance of our best current model for as long as we can thanks to
compute donation from Stability AI via LAION!

</details>

<details>
<summary>

### What hardware will be required to run the models?

</summary>

The current smallest (Pythia) model is 12B parameters and is challenging to run
on consumer hardware, but can run on a single professional GPU. In future there
may be smaller models and we hope to make progress on methods like integer
quantisation which can help run the model on smaller hardware.

</details>

<details>
<summary>

### How can I contribute?

</summary>

If you want to help in the data collection for training the model, go to the
website [https://open-assistant.io/](https://open-assistant.io/).

If you want to contribute code, take a look at the
[tasks in GitHub](https://github.com/orgs/LAION-AI/projects/3) and comment on an
issue stating your wish to be assigned. You can also take a look at this
[contributing guide](https://github.com/LAION-AI/Open-Assistant/blob/main/CONTRIBUTING.md).

</details>

<details>
<summary>

### What technologies are used?

</summary>

The Python backend for the data collection app as well as for the inference
backend uses FastAPI. The frontend is built with NextJS and Typescript.

The ML codebase is largely PyTorch-based and uses HuggingFace Transformers as
well as accelerate, DeepSpeed, bitsandbytes, NLTK, and other libraries.

</details>

## Questions about the data collection website

<details>
<summary>

### Can I use ChatGPT to help in training Open Assistant, for instance, by generating answers?

</summary>

No, it is against their terms of service to use it to help train other models.
See
[this issue](https://github.com/LAION-AI/Open-Assistant/issues/471#issuecomment-1374392299).
ChatGPT-like answers will be removed.

</details>

<details>
<summary>

### What should I do if I don't know how to complete the task as an assistant?

</summary>
Skip it.
</details>

<details>
<summary>

### Should I fact check the answers by the assistant?

</summary>

Yes, you should try. If you are not sure, skip the task.

</details>

<details>
<summary>

### How can I see my score?

</summary>

In your [account settings](https://open-assistant.io/account).

</details>

<details>
<summary>

### Can we see how many data points have been collected?

</summary>

You can see a regularly updated interface at
[https://open-assistant.io/stats](https://open-assistant.io/stats).

</details>

<details>
<summary>

### How do I write and label prompts?

</summary>

Check the
[guidelines](https://projects.laion.ai/Open-Assistant/docs/guides/guidelines).

</details>

<details>
<summary>

### Where can I report a bug or create a new feature request?

</summary>

In the [GitHub issues](https://github.com/LAION-AI/Open-Assistant/issues).

</details>

<details>
<summary>

### Why am I not allowed to write about this topic, even though it isn't illegal?

</summary>

We want to ensure that the Open Assistant dataset is as accessible as possible.
As such, it's necessary to avoid any harmful or offensive content that could be
grounds for removal on sites such as Hugging Face. Likewise, we want the model
to be trained to reject as few questions as possible, so it's important to not
include prompts that leave the assistant with no other choice but to refuse in
order to avoid the generation of harmful content.

</details>

## Questions about the development process

<details>
<summary>

### Docker-Compose instead of Docker Compose

</summary>

If you are using `docker-compose` instead of `docker compose` (note the " "
instead of the "-"), you should update your docker cli to the latest version.
`docker compose` is the most recent version and should be used instead of
`docker-compose`.

For more details and information check out
[this StackOverflow thread](https://stackoverflow.com/questions/66514436/difference-between-docker-compose-and-docker-compose)
that explains it all in detail.

</details>

<details>
<summary>

### Enable Docker's BuildKit Backend

</summary>

[BuildKit](https://docs.docker.com/build/buildkit/) is Docker's new and improved
builder backend. In addition to being faster and more efficient, it supports
many new features, among which is the ability to provide a persistent cache,
which outlives builds, to compilers and package managers. This is very useful to
speed up consecutive builds, and is used by some container images of
OpenAssistant's stack.

The BuildKit backend is used by
[default by Compose V2](https://www.docker.com/blog/announcing-compose-v2-general-availability/)
(see above). <br/> But if you want to build an image with `docker build` instead
of `docker compose build`, you might need to enable BuildKit.

To do so, just add `DOCKER_BUILDKIT=1` to your environment.

For instance:

```shell
export DOCKER_BUILDKIT=1
```

You could also, more conveniently,
[enable BuildKit by default](https://docs.docker.com/build/buildkit/#:~:text=To%20enable%20docker%20BuildKit%20by%20default),
or use
[Docker Buildx](https://docs.docker.com/build/#:~:text=The%20new%20client%20Docker%20Buildx).

</details>

<details>
<summary>

### Pre-commit

</summary>

We are using pre-commit to ensure the quality of the code as well as the same
code standard.

The steps that you need to follow to be able to use it are:

```bash
# install the pre-commit Python package
pip3 install pre-commit

# install pre-commit to the Git repo to run automatically on commit
pre-commit install
```

So from now on, in your next commits it will run the `pre-commit` on the files
that have been staged. Most formatting issues are automatically resolved by the
hooks so the files can simply be re-added and you can commit. Some issues may
require manual resolution.

If you wish to run pre-commit on all files, not just ones your last commit has
modified, you can use `pre-commit run --all-files`.

</details>

<details>
<summary>

### Docker Cannot Start Container: Permission Denied

</summary>

Instead of running docker with the root command always, you could create a
`docker` group with granted permissions (root):

```bash
# Create new linux user
sudo groupadd docker

# Add the actual user to the group
sudo usermod -aG docker $USER

# Log in the group (apply the group changes to actual terminal session)
newgrp docker
```

After that, you should be able to run docker: `docker run .`. In the case you
still are not able, can try to reboot terminal:

```bash
reboot
```

</details>

<details>
<summary>

### Docker Cannot Stop Container

</summary>

If you try to shut down the services (`docker-compose down`), and you are
getting permission denied (using root user), you can try the following:

```bash
# Restart docker daemon
sudo systemctl restart docker.socket docker.service

# And remove the container
docker rm -f <container id>
```

</details>

<details>
<summary>

### Docker Port Problems

</summary>

Oftentimes people already have some Postgres instance running on the dev
machine. To avoid port problems, change the ports in the `docker-compose.yml` to
ones excluding `5433`, like:

1. Change `db.ports` to `- 5431:5431`.
2. Add `POSTGRES_PORT: 5431` to `db.environment`
3. Change `webdb.ports` to `- 5432:5431`
4. Add `POSTGRES_PORT: 5431` to `db.environment`
5. Add `- POSTGRES_PORT=5432` to `backend.environment`
6. Change `web.environment.DATABASE_URL` to
   `postgres://postgres:postgres@webdb:5432/oasst_web`

</details>
