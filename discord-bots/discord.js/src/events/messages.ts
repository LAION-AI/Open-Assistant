import { Events } from "discord.js";

const msgType = {
  type: "message",
  load: async (msg) => {
    await msg.react("<a:loading:1051419341914132554>");
  },
  reply: async (msg, content) => {
    try {
      await msg.reply(content);
    } catch (err) {}

    try {
      await msg.reactions.removeAll();
    } catch (err) {}
  },
};

export default {
  name: Events.MessageCreate,
  once: false,
  async execute(message, client) {
    if (message.mentions.has(client.user) && !message.author.bot) {
      var content = message.content;
      if (message.content.includes(`<@${client.user.id}>`)) {
        if (!message.content.startsWith(`<@${client.user.id}>`)) return;
        content = message.content.split(`<@${client.user.id}> `)[1];
      }

      var commandName = content;
      var commands = await client.commands.toJSON();
      if (!commandName) commandName = "help";
      var command = client.commands.get(commandName);
      var options: any = {};
      message.user = message.author;

      if (!command) {
        commandName = "help";
        command = client.commands.get(commandName);
      }
      if (command.disablePing) return;
      var guildId;
      if (message.guild) guildId = message.guild.id;
      try {
        await command.execute(message, client, commands, msgType, options);
      } catch (error) {
        try {
          await message.reply({
            content: "There was an error while executing this command!",
            ephemeral: true,
          });
        } catch (err) {}
      }
    }
  },
};
