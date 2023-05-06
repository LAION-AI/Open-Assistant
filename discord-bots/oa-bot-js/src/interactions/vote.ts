import {
  SlashCommandBuilder,
  ActionRowBuilder,
  ButtonStyle,
  ButtonBuilder,
} from "discord.js";
import { createInferenceClient } from "../modules/inference/client.js";
import redis from "../modules/redis.js";

export default {
  data: {
    customId: "vote",
    description: "Vote buttons for the assistant messages.",
  },
  async execute(interaction, client, messageId, voteType) {
    let chatId = await redis.get(`chat_${interaction.user.id}`);
    if (!chatId)
      return interaction.reply({
        content: "You don't have an active chat.",
        ephemeral: true,
      });
    await interaction.deferUpdate();
    var row;
    const OA = await createInferenceClient(
      interaction.user.username,
      interaction.user.id
    );
    let score = 0;
    if (voteType == "up") {
      score = 1;
      row = new ActionRowBuilder().addComponents(
        new ButtonBuilder()
          .setStyle(ButtonStyle.Primary)
          .setLabel(`👍`)
          .setDisabled(true)
          .setCustomId(`vote__up`),
        new ButtonBuilder()
          .setStyle(ButtonStyle.Secondary)
          .setLabel(`👎`)
          .setDisabled(true)
          .setCustomId(`vote__down`)
      );
    }
    if (voteType == "down") {
      row = new ActionRowBuilder().addComponents(
        new ButtonBuilder()
          .setStyle(ButtonStyle.Secondary)
          .setLabel(`👍`)
          .setDisabled(true)
          .setCustomId(`vote__up`),
        new ButtonBuilder()
          .setStyle(ButtonStyle.Primary)
          .setLabel(`👎`)
          .setDisabled(true)
          .setCustomId(`vote__down`)
      );
    }
    let vote = await OA.vote({
      chat_id: chatId,
      message_id: messageId,
      score: score,
    });
    console.log(vote);

    await interaction.editReply({
      components: [row],
    });
  },
};
