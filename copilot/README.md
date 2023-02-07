# Deploying on AWS

## Introduction

[Copilot](https://aws.github.io/copilot-cli/) helps simplify AWS resources and
automate deploymnents for projects.

This sample configuration runs the Open Assistant web app as an ECS Fargate
services backed by a Serverless Aurora Postgres database.

## To Setup

Setup requires a few steps:

```sh
copilot app init --domain your_domain.com
```

This will initialize and register a variety of URLs with your `your_domain.com`.
Replace with a proper domain to setup SSL certificates.

```sh
copilot env deploy
```

This will create a variety of aws roles and services needed for deployment.

```sh
copilot deploy
```

This will deploy the services but it won't be 100% ready for usage. Before being
ready, we have to inspect the AWS Secrets manager and extract out the database
credentials. Read those credentials then put them, and a few other secrets, in a
`secrets.yml` file like the following:

```yaml
DATABASE_URL:
  staging: postgres://postgres:${db_password}@${db_host}:${db_port}/${db_name}
DISCORD_CLIENT_ID:
  staging: ...
DISCORD_CLIENT_SECRET:
  staging: ...
EMAIL_SERVER_HOST:
  staging: ...
EMAIL_SERVER_PORT:
  staging: ...
EMAIL_SERVER_USER:
  staging: ...
EMAIL_SERVER_PASSWORD:
  staging: ...
EMAIL_FROM:
  staging: ...
FASTAPI_URL:
  staging: ...
FASTAPI_KEY:
  staging: ...
NEXTAUTH_SECRET:
  staging: ...
```

Then, upload the secrets to AWS with:

```sh
copilot secret init --cli-input-yaml secrets.yml
```

Now, finally deploy:

```sh
copilot deploy
```

If we documented everything correctly, the site should work properly.

## To Update Manually

First, make sure the database is updated with any schema changes:

```sh
copilot task run \
    --app open-assistant --env staging \
    -n prisma-push \
    --dockerfile docker/Dockerfile.prisma --build-context "./" \
    --secrets DATABASE_URL=/copilot/open-assistant/staging/secrets/DATABASE_URL
```

Next, deploy everything:

```sh
copilot deploy
```

TODO: Make this a pipeline once github and aws are fully connected.
