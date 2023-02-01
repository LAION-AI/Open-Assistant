### Docker-Compose instead of Docker Compose

If you are using `docker-compose` instead of `docker compose` (note the " "
instead of the "-"), you should update your docker cli to the latest version.
`docker compose` is the most recent version and should be used instead of
`docker-compose`

For more details and information check out
[this SO thread](https://stackoverflow.com/questions/66514436/difference-between-docker-compose-and-docker-compose)
that explains it all in detail.

### Enable Docker's BuildKit Backend

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

### Pre-commit

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

## Docker Cannot Start Container: Permission Denied

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

### Docker Cannot Stop Container

If you try to shut down the services (`docker-compose down`), and you are
getting permission denied (using root user), you can try the following:

```bash
    # Restart docker daemon
    sudo systemctl restart docker.socket docker.service

    # And remove the container
    docker rm -f <container id>
```

### Docker Port Problems

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
