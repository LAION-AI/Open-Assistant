# Frequently Asked Questions

In this page, there are some of the most frequently asked questions.

## Questions about the project

<details>
<summary>

### How far along is this project?

</summary>

We are in the early stages of development, working from established research in
applying RLHF to large language models.

</details>

<details>
<summary>

### Can I install Open Assistant locally and chat with it?

</summary>

The project is not at that stage yet. See
[the plan](https://github.com/LAION-AI/Open-Assistant#the-plan).

</details>

<details>
<summary>

### What is the Docker command for?

</summary>

Only for local development. It does not launch an AI model.

</details>

<details>
<summary>

### Is an AI model ready to test yet?

</summary>

Not yet. The data you help us collect now through
[https://open-assistant.io/](https://open-assistant.io/) will be used to improve
it.

</details>

<details>
<summary>

### What license does Open Assistant use?

</summary>

The code and models are licensed under the Apache 2.0 license.

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

It's still being discussed. Options include Pythia, GPT-J, and a bunch more..
You can follow the discussion in the Discord channel
[#data-discussion](https://discord.com/channels/1055935572465700980/1058348535612985394).

</details>

<details>
<summary>

### Can I download the data?

</summary>

You will be able to, under CC BY 4.0, but it's not released yet. We want to
remove spam and PII before releasing it.

</details>

<details>
<summary>

### Who is behind Open Assistant?

</summary>

Open Assistant is a project organized by [LAION](https://laion.ai/) and
individuals around the world interested in bringing this technology to everyone.

</details>

<details>
<summary>

### Will Open Assistant be free?

</summary>

Yes, Open Assistant will be free to use and modify.

</details>

<details>
<summary>

### What hardware will be required to run the models?

</summary>
There will be versions which will be runnable on consumer hardware.

</details>

<details>
<summary>

### How can I contribute?

</summary>

If you want to help in the data collection for training the model, go to the
website [https://open-assistant.io/](https://open-assistant.io/). If you want to
contribute code, take a look at the
[tasks in GitHub](https://github.com/orgs/LAION-AI/projects/3) and grab one.
Take a look at this
[contributing guide](https://github.com/LAION-AI/Open-Assistant/blob/main/CONTRIBUTING.md).

</details>

## Questions about the model training website

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

There's no public interface for that yet. However, some updates are posted
periodically in
[the #data-updates Discord channel](https://discord.com/channels/1055935572465700980/1073706683068596394)

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

## Questions about developing

<details>
<summary>

### Docker-Compose instead of Docker Compose

</summary>

If you are using `docker-compose` instead of `docker compose` (note the " "
instead of the "-"), you should update your docker cli to the latest version.
`docker compose` is the most recent version and should be used instead of
`docker-compose`.

For more details and information check out
[this SO thread](https://stackoverflow.com/questions/66514436/difference-between-docker-compose-and-docker-compose)
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
    # install pre-commit in your python environment
    pip3 install pre-commit

    # install pre-commit in your github configuration
    pre-commit install
```

So from now on, in your next commits it will run the `pre-commit` on the files
that have been staged. If there has been any error, you will need to solve that,
and then stage+commit again the changes.

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
