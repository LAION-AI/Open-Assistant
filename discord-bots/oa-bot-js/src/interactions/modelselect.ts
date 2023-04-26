import {
  SlashCommandBuilder,
  ActionRowBuilder,
  StringSelectMenuBuilder,
  StringSelectMenuOptionBuilder,
} from "discord.js";
import { createInferenceClient } from "../modules/inference/client.js";
import redis from "../modules/redis.js";

export default {
  data: {
    customId: "modelselect",
    description: "Switch to another model.",
  },
  async execute(interaction, client) {
    // get selected value
    let model = interaction.values[0];
    // set model
    await interaction.deferReply({
      ephemeral: true,
    });
    redis.set(`model_${interaction.user.id}`, model);
    await interaction.editReply({
      content: `Model set to ${model}.`,
      ephemeral: true,
    });
  },
};
