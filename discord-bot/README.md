# Open-Assistant Data Collection Discord Bot

This bot collects human feedback to create a dataset for RLHF-alignment of an
assistant chat bot based on a large language model. You and other people can
teach the bot how to respond to user requests by demonstration and by ranking
the bot's outputs. If you want to learn more about RLHF please refer
[to OpenAI's InstructGPT blog post](https://openai.com/blog/instruction-following/).

## Invite official bot

To add the official Open-Assistant data collection bot to your discord server
[click here](https://discord.com/api/oauth2/authorize?client_id=1054078345542910022&permissions=1634235579456&scope=bot%20applications.commands).
The bot needs access to read the contents of user text messages.

## Contributing

If you are unfamiliar with `hikari`, `lightbulb`, or `miru`, please refer to the
[large list of examples](https://gist.github.com/AlexanderHOtt/7805843a7120f755938a3b75d680d2e7)

### Bot Setup

1. Create a new discord application at the
   [Discord Developer Portal](https://discord.com/developers/applications)

1. Go to the "Bot" tab and create a new bot

1. Scroll down to "Privileged Gateway Intents" and enable the following options:

   - Server Members Intent
   - Presence Intent
   - Message Content Intent

This page also contains the bot token, which you will need to add to the `.env`
file later.

2. Go to the "OAuth2" tab scroll to "Default Authorization Link"

3. Set "AUTHORIZATION METHOD" to "In-app Authorization"

4. Select the "bot" and "applications.commands" scopes

5. For testing and local development, it's easiest to set "BOT PERMISSIONS" to
   "Administrator"

Remember to save your changes.

6. Copy the "CLIENT ID" from the top of the page and replace it in the link
   below to invite your bot.

```
https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID_HERE&permissions=8&scope=bot%20applications.commands
```

### Environment Setup

To run the bot:

Install dependency module `oasst-shared`

```bash
cd oasst-shared
pip install -e .
```

```bash
cp .env.example .env

# edit .env and add your bot token and other values
# BOT_TOKEN is given by the discord developer portal when you create a bot
# DECLARE_GLOBAL_COMMANDS is the id of the server where you added the bot (right click on the server icon and copy id)
# OWNER_ID can be leave as an empty list

python -V  # 3.10

pip install -r requirements.txt

# in the discord-bot folder
python -m bot
```

Before you push, make sure the `pre-commit` hooks are installed and run
successfully.

```bash
pip install pre-commit
pre-commit install

...

git add .
git commit -m "<good commit message>"
# if the pre-commit fails
git add .
git commit -m "<good commit message>"
```

### Resources

#### Structure

Important files

```graphql
.env                        # Environment variables
.env.example                # Example environment variables
CONTRIBUTING.md             # This file
README.md                   # Project readme
EXAMPLES.md                 # Examples for commands and listeners
requirements.txt            # Requirements

bot/
├─  __main__.py             # Entrypoint
├─  api_client.py           # API Client for interacting with the backend
├─  bot.py                  # Main bot class
├─  settings.py             # Settings and secrets
├─  utils.py                # Utility Functions
│
├─  db/                     # Database related code
│   ├─  database.db         # SQLite database
│   ├─  schema.sql          # SQL schema
│   └─  schemas.py          # Python table schemas
│
└── extensions/             # Application logic, see https://hikari-lightbulb.readthedocs.io/en/latest/guides/extensions.html
    ├─  work.py             # Task handling logic  <-- most important file
    ├─  guild_settings.py   # Server specific settings
    └─  hot_reload.py       # Utility for hot reload extensions during development
```

#### Adding a new command/listener

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

#### Docs

Discord

- [Discord API Reference](https://discord.com/developers/docs/intro)

`hikari` (main framework)

- [Hikari Repo](https://github.com/hikari-py/hikari)
- [Hikari Docs](https://docs.hikari-py.dev/en/latest/)

`lightbulb` (command handler)

- [Lightbulb Repo](https://github.com/tandemdude/hikari-lightbulb)
- [Lightbulb Docs](https://hikari-lightbulb.readthedocs.io/en/latest/)

`miru` (component handler: buttons, modals, etc... )

- [Miru Repo](https://github.com/HyperGH/hikari-miru)
