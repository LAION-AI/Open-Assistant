# Contributing

## Setup

To run the bot

```
cp .env.example .env

python -V  # 3.10

pip install -r requirements.txt
python -m bot
```

To test the bot

```
python -m pip install -r dev-requirements.txt

nox
```

To test the bot on your own discord server you need to register a discord application at the [Discord Developer Portal](https://discord.com/developers/applications) and get at bot token.

1. Follow a tutorial on how to get a bot token, for example this one: [Creating a discord bot & getting a token](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token)
2. The bot script expects the bot token to be in the `.env` file under the `TOKEN` variable.

## Resources

Main framework

- [Hikari Repo](https://github.com/hikari-py/hikari)
- [Hikari Docs](https://docs.hikari-py.dev/en/latest/)

Command handler

- [Lightbulb Repo](https://github.com/tandemdude/hikari-lightbulb)
- [Lightbulb Docs](https://hikari-lightbulb.readthedocs.io/en/latest/)

Component handler (buttons, modals, etc... )

- [Miru Repo](https://github.com/HyperGH/hikari-miru)
