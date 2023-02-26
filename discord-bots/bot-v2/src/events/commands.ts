import { Events } from "discord.js";

const interactionType = {
  type: "interaction",
  load: async (interaction) => {
    await interaction.deferReply();
  },
  reply: async (interaction, content) => {
    if (interaction.deferred || interaction.replied) {
      await interaction.editReply(content);
    } else {
      await interaction.reply(content);
    }
  },
};

export default {
  name: Events.InteractionCreate,
  once: false,
  async execute(interaction, client) {
    if (
      !interaction.isChatInputCommand() &&
      !interaction.isContextMenuCommand()
    )
      return;
    var commands = await client.commands.toJSON();
    const command = interaction.client.commands.get(interaction.commandName);

    if (!command) {
      console.error(
        `No command matching ${interaction.commandName} was found.`
      );
      return;
    }
    var guildId;
    if (interaction.guild) guildId = interaction.guild.id;

    try {
      await command.execute(interaction, client, commands, interactionType);
    } catch (error) {
      console.log(error);
      await interactionType.reply(interaction, {
        content: "There was an error while executing this command!",
        ephemeral: true,
      });
    }
  },
};
