# Frequently Asked Questions

In this page, there are some of the most frequently asked questions.

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
