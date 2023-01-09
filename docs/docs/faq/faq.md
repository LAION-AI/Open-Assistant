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
