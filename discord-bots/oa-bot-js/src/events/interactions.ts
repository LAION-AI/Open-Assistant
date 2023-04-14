import { Events } from "discord.js";

export default {
  name: Events.InteractionCreate,
  once: false,
  async execute(interaction, client) {
    if (
      !interaction.isButton() &&
      !interaction.isStringSelectMenu() &&
      !interaction.isModalSubmit()
    )
      return;
    var id = interaction.customId;
    var arg;
    var arg2;
    var arg3;
    var arg4;
    var arg5;
    var arg6;
    if (interaction.customId.includes("_")) {
      id = interaction.customId.split("_")[0];
      arg = interaction.customId.split("_")[1];
      arg2 = interaction.customId.split("_")[2];
      arg3 = interaction.customId.split("_")[3];
      arg4 = interaction.customId.split("_")[4];
      arg5 = interaction.customId.split("_")[5];
      arg6 = interaction.customId.split("_")[6];
    }
    const interact = interaction.client.interactions.get(id);

    if (!interact) {
      console.error(
        `No interaction matching ${interaction.customId} was found.`
      );
      return;
    }

    try {
      await interact.execute(
        interaction,
        client,
        arg,
        arg2,
        arg3,
        arg4,
        arg5,
        arg6
      );
    } catch (error) {
      console.error(error);
      await interaction.reply({
        content: "There was an error while executing this interaction!",
        ephemeral: true,
      });
    }
  },
};
