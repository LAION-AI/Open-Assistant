import {
  EmbedBuilder,
  ButtonBuilder,
  ButtonStyle,
  ActionRowBuilder,
  StringSelectMenuBuilder,
} from "discord.js";
import { getLocaleDisplayName, locales } from "../langs.js";

export async function infoInteraction(translation, interaction, lang) {
  var embed = new EmbedBuilder()
    .setColor("#3a82f7")
    .setTimestamp()
    .setTitle("Open assistant Info")
    .setDescription(
      `${translation.blurb}${translation.blurb1}${translation.description}\n**${translation.faq_title}**`
    )
    .setFields(
      {
        name: translation.faq_items.q0,
        value: translation.faq_items.a0,
      },
      {
        name: translation.faq_items.q1,
        value: translation.faq_items.a1,
      },
      {
        name: translation.faq_items.q2,
        value: translation.faq_items.a2,
      },
      {
        name: translation.faq_items.q3,
        value: translation.faq_items.a3,
      },
      {
        name: translation.faq_items.q4,
        value: translation.faq_items.a4,
      },
      {
        name: translation.faq_items.q5,
        value: translation.faq_items.a5,
      }
    )
    .setURL("https://open-assistant.io/?ref=turing")
    .setFooter({ text: `${getLocaleDisplayName(lang)}` })
    .setThumbnail("https://open-assistant.io/images/logos/logo.png");
  const row = new ActionRowBuilder().addComponents(
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
