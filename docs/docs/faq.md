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

We are in the early stages of development, generally following the process
outlined in the InstructGPT paper. We have candidate supervised finetuning (SFT)
models but we have not begun to apply Reinforcement Learning from Human Feedback
(RLHF) yet.

</details>

<details>
<summary>

### Can I install Open Assistant locally and chat with it?

</summary>

The candidate SFT models are
[available on HuggingFace](https://huggingface.co/OpenAssistant) and can be
loaded via the HuggingFace Transformers library. As such you may be able to use
them with sufficient hardware. There are also spaces on HF which can be used to
chat with the OA candidate without your own hardware. However, these models are
not final and can produce poor or undesirable outputs.

</details>

<details>
<summary>

### Is an AI model ready to test yet?

</summary>

You can help test the outputs from the initial SFT candidate models by ranking
assistant replies at [https://open-assistant.io/](https://open-assistant.io/).
These rankings will be used to produce improved models.

</details>

<details>
<summary>

### What is the Docker command for?

</summary>

The `docker compose` command in the README is for setting up the project for
local development on the website or data collection backend. It does not launch
an AI model or the inference server.

</details>

<details>
<summary>

### What license does Open Assistant use?

</summary>

The code and models are licensed under the Apache 2.0 license. This means they
will be available for a wide range of uses including commercial use.

</details>

<details>
<summary>

### Is the model open?

</summary>

The model will be open. Some very early prototype models are published on
HuggingFace. Follow the discussion in the Discord channel
[#ml-models-demo](https://discord.com/channels/1055935572465700980/1067096888530178048).

</details>

<details>
<summary>

### Which base model will be used?

</summary>

It's not finalised, but early candidate models are being tuned from Pythia. This
may change in the future.

</details>

<details>
<summary>

### Can I download the data?

</summary>

You will be able to, under CC BY 4.0, but it's not released yet. We want to
remove spam and PII before releasing it. Some cherrypicked samples which are
confirmed to be safe are available in the `oasst-model-eval`
[repository](https://github.com/Open-Assistant/oasst-model-eval).

</details>

<details>
<summary>

### Who is behind Open Assistant?

</summary>

Open Assistant is a project organized by [LAION](https://laion.ai/) and
individuals around the world interested in bringing this technology to everyone.

The project would not be possible without the many volunteers who have spent
time contributing both to data collection and to the development process.

</details>

<details>
<summary>

### Will Open Assistant be free?

</summary>

Yes, the model code, weights, and data will be released for free. We also hope
to host a free public instance of the final model.

</details>

<details>
<summary>

### What hardware will be required to run the models?

</summary>

There will likely be multiple sizes of model, the smallest of which should be
able to run on consumer hardware. Relatively high-end consumer hardware may be
required. It is possible that future open-source developments from the community
will bring down requirements after the model is published, but this cannot be
guaranteed.

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
