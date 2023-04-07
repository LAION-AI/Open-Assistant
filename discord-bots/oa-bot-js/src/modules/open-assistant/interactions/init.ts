import {
  EmbedBuilder,
  ButtonBuilder,
  ButtonStyle,
  ActionRowBuilder,
} from "discord.js";
import { getLocaleDisplayName } from "../langs.js";

export async function initInteraction(interaction, translation, lang) {
  var embed = new EmbedBuilder()
    .setColor("#3a82f7")
    .setTimestamp()
    .setFooter({ text: `${getLocaleDisplayName(lang)}` })
    .setTitle("Open assistant")
    .setDescription(`${translation["conversational"]}`)
    .setURL("https://open-assistant.io/?ref=turing")
    .setThumbnail("https://open-assistant.io/images/logos/logo.png");

  const row = new ActionRowBuilder().addComponents(
    new ButtonBuilder()
      .setLabel(translation.about)
      .setCustomId(`oa_info_n_${interaction.user.id}`)
      .setStyle(ButtonStyle.Primary),
    new ButtonBuilder()
      .setLabel(translation.grab_a_task)
      .setCustomId(`oa_tasks_n_${interaction.user.id}`)
      .setStyle(ButtonStyle.Primary)
      .setDisabled(false),
    new ButtonBuilder()
      .setLabel("Change language")
      .setCustomId(`oa_lang-btn_n_${interaction.user.id}`)
      .setStyle(ButtonStyle.Secondary)
      .setDisabled(false)
  );
  await interaction.editReply({
    embeds: [embed],
    components: [row],
  });
}
