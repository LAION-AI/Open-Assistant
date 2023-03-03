import {
  EmbedBuilder,
  ButtonBuilder,
  ButtonStyle,
  ActionRowBuilder,
} from "discord.js";
import OpenAssistant from "open-assistant.js";
import { getLocaleDisplayName } from "../langs.js";
import { formatTaskType } from "../tasks.js";
var oa: OpenAssistant = new OpenAssistant(
  process.env.OA_APIKEY,
  process.env.OA_APIURL
);
export async function taskInteraction(
  interaction,
  lang,
  user,
  translation,
  client
) {
  /*var ispremium = await isPremium(interaction.user.id, interaction.guildId);
      if (!ispremium) {
        await interaction.editReply({
          ephemeral: true,
          content: `This feature is only for premium users.`,
        });
        return;
      }*/

  var task = await oa.getTask({
    type: "random",
    user: user,
    collective: false,
    lang: lang,
  });
  client.tasks.push(task);
  if (task.message) {
    var embd = await sendErr(task.message);
    await interaction.editReply({
      embeds: [embd],
      components: [],
    });
    return;
  }
  var embeds = [];
  var embed = new EmbedBuilder()
    .setColor("#3a82f7")
    .setTimestamp()
    .setThumbnail("https://open-assistant.io/images/logos/logo.png")
    .setFooter({ text: `${getLocaleDisplayName(lang)}` })
    .setTitle(`${translation[formatTaskType(task.type)].label}`)
    .setDescription(`${translation[formatTaskType(task.type)].overview}`);
  var rows = [];
  const row = new ActionRowBuilder();

  if (
    task.type == "initial_prompt" ||
    task.type == "assistant_reply" ||
    task.type == "prompter_reply"
  ) {
    row.addComponents(
      new ButtonBuilder()
        .setCustomId(`oa_text-modal_${task.id}_${interaction.user.id}`)
        .setLabel(`${translation[formatTaskType(task.type)].label}`)
        .setStyle(ButtonStyle.Primary)
    );
    embeds.push(embed);
    if (task.type == "assistant_reply" || task.type == "prompter_reply") {
      task.conversation.messages.forEach((x, i) => {
        var username = "User";
        if (x.is_assistant) username = "AI";

        var emb = new EmbedBuilder()
          .setAuthor({
            iconURL: `${
              username == "User"
                ? "https://open-assistant.io/images/temp-avatars/av1.jpg"
                : "https://open-assistant.io/images/logos/logo.png"
            }`,
            name: username,
          })
          .setDescription(x.text)
          .setFooter({ text: x.frontend_message_id });
        if (i == task.conversation.messages.length - 1) {
          emb.setColor("#3a82f7");
        }
        embeds.push(emb);
      });
    }
  } else {
    row.addComponents(
      new ButtonBuilder()
        .setCustomId(`oa_label_${task.id}_${interaction.user.id}`)
        .setLabel(`${translation[formatTaskType(task.type)].label}`)
        .setStyle(ButtonStyle.Primary)
    );
    embeds.push(embed);
    task.conversation.messages.forEach((x, i) => {
      var username = "User";
      if (x.is_assistant) username = "AI";

      var emb = new EmbedBuilder()
        .setAuthor({
          iconURL: `${
            username == "User"
              ? "https://open-assistant.io/images/temp-avatars/av1.jpg"
              : "https://open-assistant.io/images/logos/logo.png"
          }`,
          name: username,
        })
        .setDescription(x.text)
        .setFooter({ text: x.frontend_message_id });
      if (i == task.conversation.messages.length - 1) {
        emb.setColor("#3a82f7");
      }
      embeds.push(emb);
    });
  }
  row.addComponents(
    new ButtonBuilder()
      .setCustomId(`oa_skip_${task.id}_${interaction.user.id}`)
      .setLabel(`${translation.skip}`)
      .setStyle(ButtonStyle.Danger),
    new ButtonBuilder()
      .setLabel("Change language")
      .setCustomId(`oa_lang-btn_n_${interaction.user.id}`)
      .setStyle(ButtonStyle.Secondary)
      .setDisabled(false)
  );
  rows.push(row);
  await interaction.editReply({
    components: rows,
    embeds: embeds,
  });
}
async function sendErr(err: string) {
  var embed = new EmbedBuilder()
    .setColor("#F73A3A")
    .setDescription(err)
    .setTimestamp();
  return embed;
}
