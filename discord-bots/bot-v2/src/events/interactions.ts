import { Events } from "discord.js";
import chalk from "chalk";

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
    var args = interaction.customId.split("_");
    const interact = interaction.client.interactions.get(id);

    if (!interact) {
      console.error(
        `No interaction matching ${interaction.customId} was found.`
      );
      return;
    }

    try {
      await interact.execute(interaction, client, ...args);
    } catch (error) {
      console.error(error);
      await interaction.reply({
        content: "There was an error while executing this interaction!",
        ephemeral: true,
      });
    }
  },
};
