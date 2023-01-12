### Docker-Compose instead of Docker Compose

If you are using `docker-compose` instead of `docker compose` (note the " "
instead of the "-"), you should update your docker cli to the latest version.
`docker compose` is the most recent version and should be used instead of
`docker-compose`

For more details and information check out
[this SO thread](https://stackoverflow.com/questions/66514436/difference-between-docker-compose-and-docker-compose)
that explains it all in detail.

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
