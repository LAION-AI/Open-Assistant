### Docker-Compose instead of Docker Compose

If you have installed the version of `docker-compose` instead of
`docker compose`, you might have to do some changes in the commands:

```bash
    # docker compose up backend-dev --build --attach-dependencies
    docker-compose up --build --attach-dependencies backend-dev     # starting only backend-dev

    # docker compose up --build
    docker-compose up --build                                       # starting the all services
```

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
