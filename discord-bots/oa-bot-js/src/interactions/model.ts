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
    customId: "model",
    description: "Switch to another model.",
  },
  async execute(interaction, client, userId) {
    if (interaction.user.id != userId)
      return interaction.reply({
        content: "You don't have permission to do this.",
        ephemeral: true,
      });
    // model selector
    let row = new ActionRowBuilder().addComponents(
      new StringSelectMenuBuilder()
        .setCustomId("modelselect")
        .setPlaceholder("Select a model")
        .setMinValues(1)
        .setMaxValues(1)
        .addOptions(
          new StringSelectMenuOptionBuilder()
            .setLabel("OA_SFT_Llama_30B")
            .setDescription("Llama (default)")
            .setValue("OA_SFT_Llama_30B"),
          new StringSelectMenuOptionBuilder()
            .setLabel("oasst-sft-4-pythia-12b")
            .setDescription("Pythia")
            .setValue("OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5")
        )
    );
    await interaction.reply({
      content: "Select a model.",
      components: [row],
      ephemeral: true,
    });
  },
};
