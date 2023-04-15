import { Events } from "discord.js";

const msgType = {
  type: "message",
  load: async (msg) => {
    await msg.react("<a:loading:1051419341914132554>");
    try {
      await msg.channel.sendTyping();
    } catch (err) {}
  },
  reply: async (msg, content) => {
    try {
      const userReactions = msg.reactions.cache.filter((reaction) =>
        reaction.users.cache.has(process.env.CLIENT_ID)
      );
      try {
        for (const reaction of userReactions.values()) {
          reaction.users.remove(process.env.CLIENT_ID);
        }
      } catch (error) {
        console.error("Failed to remove reactions:", error);
      }

      return await msg.reply(content);
    } catch (err) {
      console.log(err);
    }
  },
};

export default {
  name: Events.MessageCreate,
  once: false,
  async execute(message, client) {
    if (message.mentions.has(client.user) && !message.author.bot) {
      var content = message.content;
      // if is ping by @everyone or @here or @role ignore
      if (
        message.content.includes("@everyone") ||
        message.content.includes("@here") ||
        message.content.includes("<@&")
      )
        return;
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
        commandName = "chat";
        command = client.commands.get(commandName);
      }
      if (commandName == "chat" || content.startsWith("chat ")) {
        options.message = content.replace("chat ", "");
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
