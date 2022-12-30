# Contributing

## Setup

To run the bot

```
cp .env.example .env

python -V  # 3.10

pip install -r requirements.txt
python -m bot
```

Before you push, make sure the `pre-commit` hooks are installed and run successfully.

```
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

To test the bot on your own discord server you need to register a discord application at the [Discord Developer Portal](https://discord.com/developers/applications) and get at bot token.

1. Follow a tutorial on how to get a bot token, for example this one: [Creating a discord bot & getting a token](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token)
2. The bot script expects the bot token to be in the `.env` file under the `TOKEN` variable.

## Resources

### Structure

```graphql
.env                        # Environment variables
.env.example                # Example environment variables
CONTRIBUTING.md             # This file
dev-requirements.txt        # Development requirements
flake8-requirements.txt     # Flake8 extensions (for linting)
noxfile.py                  # Nox session definitions (for formatting, typechecking, linting)
pyproject.toml              # Project configuration
README.md                   # Project readme
requirements.txt            # Requirements
templates/                  # Message templates

bot/
├─  __init__.py
├─  __main__.py         # Entrypoint
├─  bot.py              # Main bot class
├─  config.py           # Configuration and secrets
├─  utils.py            # Utility Functions
│
├─  db/                 # Database related code
│   ├─  database.db     # SQLite database
│   └─  schema.sql      # Database schema
│
└── extensions/         # Application logic, see https://hikari-lightbulb.readthedocs.io/en/latest/guides/extensions.html
    └─   hot_reload.py  # Utility for hot reload extension
```

### Adding a new command/listener

1. Create a new file in the `extensions` folder
2. Copy the template below

```py
# -*- coding: utf-8 -*-
"""My plugin."""
import lightbulb

plugin = lightbulb.Plugin("MyPlugin")

# Add your commands here

def load(bot: lightbulb.BotApp):
    """Add the plugin to the bot."""
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    """Remove the plugin to the bot."""
    bot.remove_plugin(plugin)
```

For example commands and listeners, see [EXAMPLES.md](/discord-bot/EXAMPLES.md)

### Docs

Discord

- [Discord API Reference](https://discord.com/developers/docs/intro)

Main framework

- [Hikari Repo](https://github.com/hikari-py/hikari)
- [Hikari Docs](https://docs.hikari-py.dev/en/latest/)

Command handler

- [Lightbulb Repo](https://github.com/tandemdude/hikari-lightbulb)
- [Lightbulb Docs](https://hikari-lightbulb.readthedocs.io/en/latest/)

Component handler (buttons, modals, etc... )

- [Miru Repo](https://github.com/HyperGH/hikari-miru)
