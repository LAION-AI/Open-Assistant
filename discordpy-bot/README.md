# Open-Assistant Data Collection Discord Bot

This bot collects human feedback to create a dataset for RLHF-alignment of an
assistant chat bot based on a large language model. You and other people can
teach the bot how to respond to user requests by demonstration and by ranking
the bot's outputs. If you want to learn more about RLHF please refer
[to OpenAI's InstructGPT blog post](https://openai.com/blog/instruction-following/).

## Invite official bot

To add the official Open-Assistant data collection bot to your discord server
(TODO: missing invite link).
The bot needs access to read the contents of user text messages.

## Contributing

If you are unfamiliar with `discord.py`, please refer to the
[Docs](https://discordpy.readthedocs.io/en/stable/quickstart.html).

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

# run the bot
python -m discordpy-bot
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

discordpy-bot/
├─  __main__.py             # Entrypoint
├─  (TODO: insert more structure here)

```

#### Adding a new command/listener

1. TODO: write docs for this

#### Docs

TODO: add/link docs and resources
