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

This project has concluded. We have released supervised finetuning (SFT) models
using Llama 2, LLaMa, Falcon, Pythia, and StabeLM as well as reinforcement
learning from human feedback trained models and reward models, all of which are
available at [here](https://huggingface.co/OpenAssistant). In addition to our
models, we have released three datasets from OpenAssistant conversations, and a
[research paper](https://arxiv.org/abs/2304.07327).

</details>

<details>
<summary>

### Is a model ready to test yet?

</summary>

Our online demonstration is no longer available, but the models remain available
to download [here](https://huggingface.co/OpenAssistant).

</details>

<details>
<summary>

### Can I install Open Assistant locally and chat with it?

</summary>

All of our models are
[available on HuggingFace](https://huggingface.co/OpenAssistant) and can be
loaded via the HuggingFace Transformers library or other runners if converted.
As such you may be able to use them with sufficient hardware. There are also
spaces on HF which can be used to chat with the OA candidate without your own
hardware. However, some of these models are not final and can produce poor or
undesirable outputs.

LLaMa (v1) SFT models cannot be released directly due to Meta's license but XOR
weights are released on the HuggingFace org. Follow the process in the README
there to obtain a full model from these XOR weights. Llama 2 models are not
required to be XORed.

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

Open Assistant models are released under the license of their respective base
models, be that Llama 2, Falcon, Pythia, or StableLM. LLaMa (not 2) models are
only released as XOR weights, meaning you will need the original LLaMa weights
to use them.

The Open Assistant data is released under Apache-2.0 allowing a wide range of
uses including commercial use.

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

The model code, weights, and data are free. Our free public instance of our best
models is not longer available due to the project's conclusion.

</details>

<details>
<summary>

### What hardware will be required to run the models?

</summary>

The current smallest models are 7B parameters and are challenging to run on
consumer hardware, but can run on a single professional GPU or be quantized to
run on more widely available hardware.

</details>

<details>
<summary>

### How can I contribute?

</summary>

This project has now concluded.

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
