# Open-Assistant Data Collection Discord Bot

This bot collects human feedback to create a dataset for RLHF-alignment of an assistant chat bot based on a large langugae model. You and other people can teach the bot how to respond to user requests by demonstration and by garding and ranking the bot's outputs. If you want to learn more about RLHF please refer [to OpenAI's InstructGPT blog post](https://openai.com/blog/instruction-following/).

## Invite official bot

To add the official Open-Assistant data collection bot to your discord server [click here](https://discord.com/api/oauth2/authorize?client_id=1054078345542910022&permissions=1634235579456&scope=bot). The bot needs access to read the contents of user text messages.

## Bot token for development

To test the bot on your own discord server you need to register a discord application at the [Discord Developer Portal](https://discord.com/developers/applications) and get at bot token.

1. Follow a tutorial on how to get a bot token, for example this one: [Creating a discord bot & getting a token](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token)
2. The bot script expects the bot token to be in an environment variable called `BOT_TOKEN`.

The simplest way to configure the token is via an `.env` file:

```
BOT_TOKEN=XYZABC123...
```
