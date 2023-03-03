import {
  EmbedBuilder,
  ButtonBuilder,
  ButtonStyle,
  ActionRowBuilder,
} from "discord.js";
import { getLocaleDisplayName, getTranlation } from "../langs.js";
import { formatTaskType } from "../tasks.js";
import {
  labelText,
  formatLabel,
  getLabels,
  getLabel,
  getFlags,
} from "../labels.js";
import { submitTask } from "../tasks.js";

export async function labelInteraction(
  lang,
  client,
  taskId,
  interaction,
  labelTag,
  labelValue,
  user,
  labelFlagValue
) {
  var translation = await getTranlation(lang);
  var task = client.tasks.find((x) => x.id == taskId);

  if (!task) {
    await interaction.reply({
      ephemeral: true,
      content: `Task not found, please use skip button to get a new task.`,
    });
    return;
  }
  await interaction.deferUpdate();
  var embeds = [];
  var infoEmbed = new EmbedBuilder()
    .setColor("#3a82f7")
    .setTimestamp()
    .setThumbnail("https://open-assistant.io/images/logos/logo.png")
    .setFooter({ text: `${getLocaleDisplayName(lang)}` })
    .setTitle(`${translation[formatTaskType(task.type)].label}`)
    .setDescription(`${translation[formatTaskType(task.type)].overview}`);
  embeds.push(infoEmbed);
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
  if (labelTag == "submit") {
    var solutions: any = {
      text: "",
      labels: {},
    };
    task.labels.forEach((x) => {
      if (x) {
        if (!x.value) x.value = 0;
        solutions.labels[x.name] = parseFloat(x.value);
      }
    });
    var messageId = task.message_id;
    await submitTask(
      taskId,
      user,
      interaction,
      solutions,
      lang,
      task,
      client,
      messageId
    );
    return;
  }
  if (labelTag) {
    labelTag = labelTag.replaceAll("-", "_");
    labelValue = labelValue.replaceAll("-", "_");

    if (labelTag == "flags") {
      if (
        labelValue != "skip" &&
        labelValue != "submit" &&
        !task.labels.find((x) => x.name == labelValue).value
      ) {
        task.labels.find((x) => x.name == labelValue).value = formatLabel(
          labelFlagValue,
          true
        );
      }
    } else {
      if (
        !task.labels.find((x) => x.name == labelTag).value &&
        labelValue != "skip"
      ) {
        task.labels.find((x) => x.name == labelTag).value =
          formatLabel(labelValue);
      }
    }
  }
  var label: any;
  if (labelTag == "flags") {
    label = {
      list: true,
      resultsTask: await getFlags(translation, task),
    };
  } else {
    label = await getLabel(translation, labelTag, task);
  }
  const row = new ActionRowBuilder();
  const row2 = new ActionRowBuilder();
  var rows = [];

  if (!label || labelValue == "skip" || labelValue == "submit") {
    var labels = await getLabels(task);

    var readyEmbed = new EmbedBuilder()
      .setColor("#3a82f7")
      .setTimestamp()
      .setFooter({ text: `${getLocaleDisplayName(lang)}` })
      .setTitle(`Are you sure?`)
      .addFields(
        labels.map((x) => {
          if (x) {
            var label = task.labels.find((y) => y.name == x.name);
            var value = label.value;

            if (label) {
              if (x.type == "yes/no" || x.type == "flags") {
                if (!value) task.labels.find((y) => y.name == x.name).value = 0;
                value = value == 1 ? "Yes" : "No";
              } else {
                value = `${value * 100}%`;
              }
              var name = x.name.replaceAll("_", "");
              var labelTxt = labelText(x, translation);
              if (labelTxt.question) {
                name = labelTxt.question.replaceAll(
                  "{{language}}",
                  getLocaleDisplayName(lang)
                );
              }
              if (labelTxt.max) {
                name = `${labelTxt.min}/${labelTxt.max}`;
              }

              return {
                name: `${name}`,
                value: `${value}`,
                inline: true,
              };
            }
          }
        })
      );
    row.addComponents(
      new ButtonBuilder()
        .setCustomId(`oa_label_${taskId}_${interaction.user.id}_submit`)
        .setLabel(`Submit`)
        .setStyle(ButtonStyle.Success),
      new ButtonBuilder()
        .setCustomId(`oa_label_${taskId}_${interaction.user.id}`)
        .setLabel(`Modify one`)
        .setStyle(ButtonStyle.Secondary),
      new ButtonBuilder()
        .setCustomId(`oa_skip_${task.id}_${interaction.user.id}`)
        .setLabel(`${translation.skip} task`)
        .setStyle(ButtonStyle.Danger)
    );
    await interaction.editReply({
      embeds: [readyEmbed],
      components: [row],
    });
    return;
  }
  if (label.list) {
    var flags = label.resultsTask.filter((x) => x.type == "flags");
    var embed = new EmbedBuilder()
      .setColor("#3a82f7")
      .setTimestamp()
      .setFooter({ text: `${getLocaleDisplayName(lang)}` })
      .setTitle(`${translation.label_highlighted_flag_instruction}`);
    if (labelTag != "flags") {
      embed.addFields(
        flags.map((x) => {
          return {
            name: `${x.question.replaceAll(
              "{{language}}",
              getLocaleDisplayName(lang)
            )}`,
            value: `${x.description ? x.description : "  "}`,
            inline: false,
          };
        })
      );
    }

    for (let i = 0; i < flags.length; i++) {
      let flag: any = flags[i];
      let label = task.labels.find((y) => y.name == flag.name);
      if (label) {
        flag.value = label.value;
      }
      var nextValue = flag.value == 1 ? 0 : 1;
      if (!flag.value) {
        nextValue = 1;
      }
      row.addComponents(
        new ButtonBuilder()
          .setCustomId(
            `oa_label_${task.id}_${
              interaction.user.id
            }_flags_${flag.name.replaceAll("_", "-")}_${nextValue}`
          )
          .setLabel(
            flag.question.replaceAll("{{language}}", getLocaleDisplayName(lang))
          )
          .setStyle(
            nextValue == 1 ? ButtonStyle.Secondary : ButtonStyle.Primary
          )
      );
    }
    row2.addComponents(
      new ButtonBuilder()
        .setCustomId(`oa_label_${task.id}_${interaction.user.id}_flags_submit`)
        .setLabel(`Submit flags`)
        .setStyle(ButtonStyle.Success),
      new ButtonBuilder()
        .setCustomId(`oa_label_${task.id}_${interaction.user.id}_flags_skip`)
        .setLabel(`${translation.skip} label`)
        .setStyle(ButtonStyle.Danger)
    );
    rows.push(row);
    embeds.push(embed);
  } else {
    let lbl = label.resultsTask[0];
    if (lbl.type == "yes/no") {
      var embed = new EmbedBuilder()
        .setColor("#3a82f7")
        .setTimestamp()
        .setFooter({ text: `${getLocaleDisplayName(lang)}` })
        .setTitle(
          `${lbl.question.replaceAll(
            "{{language}}",
            getLocaleDisplayName(lang)
          )}`
        );
      if (lbl.description) {
        embed.setDescription(`${lbl.description}`);
      }
      embeds.push(embed);
      row2.addComponents(
        new ButtonBuilder()
          .setCustomId(
            `oa_label_${taskId}_${interaction.user.id}_${lbl.name.replaceAll(
              "_",
              "-"
            )}_yes`
          )
          .setLabel(`✔`)
          .setStyle(ButtonStyle.Secondary),
        new ButtonBuilder()
          .setCustomId(
            `oa_label_${taskId}_${interaction.user.id}_${lbl.name.replaceAll(
              "_",
              "-"
            )}_no`
          )
          .setLabel(`❌`)
          .setStyle(ButtonStyle.Secondary)
      );
    } else if (lbl.type == "number") {
      var embed = new EmbedBuilder()
        .setColor("#3a82f7")
        .setTimestamp()
        .setFooter({ text: `${getLocaleDisplayName(lang)}` })
        .setTitle(`${lbl.min}/${lbl.max}`);
      if (lbl.description) {
        embed.setDescription(`${lbl.description}`);
      }
      embeds.push(embed);
      row.addComponents(
        new ButtonBuilder()
          .setCustomId(
            `oa_label_${taskId}_${interaction.user.id}_${lbl.name.replaceAll(
              "_",
              "-"
            )}_1`
          )
          .setLabel(`1(${lbl.min})`)
          .setStyle(ButtonStyle.Secondary),
        new ButtonBuilder()
          .setCustomId(
            `oa_label_${taskId}_${interaction.user.id}_${lbl.name.replaceAll(
              "_",
              "-"
            )}_2`
          )
          .setLabel(`2`)
          .setStyle(ButtonStyle.Secondary),
        new ButtonBuilder()
          .setCustomId(
            `oa_label_${taskId}_${interaction.user.id}_${lbl.name.replaceAll(
              "_",
              "-"
            )}_3`
          )
          .setLabel(`3`)
          .setStyle(ButtonStyle.Secondary),
        new ButtonBuilder()
          .setCustomId(
            `oa_label_${taskId}_${interaction.user.id}_${lbl.name.replaceAll(
              "_",
              "-"
            )}_4`
          )
          .setLabel(`4`)
          .setStyle(ButtonStyle.Secondary),
        new ButtonBuilder()
          .setCustomId(
            `oa_label_${taskId}_${interaction.user.id}_${lbl.name.replaceAll(
              "_",
              "-"
            )}_5`
          )
          .setLabel(`5(${lbl.max})`)
          .setStyle(ButtonStyle.Secondary)
      );
      rows.push(row);
    }
    if (labelTag || task.labels.find((x) => x.name == "spam").value) {
      row2.addComponents(
        new ButtonBuilder()
          .setCustomId(
            `oa_label_${task.id}_${interaction.user.id}_${lbl.name.replaceAll(
              "_",
              "-"
            )}_skip`
          )
          .setLabel(`${translation.skip} label`)
          .setStyle(ButtonStyle.Danger)
      );
    }
  }

  row2.addComponents(
    new ButtonBuilder()
      .setCustomId(`oa_skip_${task.id}_${interaction.user.id}`)
      .setLabel(`${translation.skip} task`)
      .setStyle(ButtonStyle.Danger),
    new ButtonBuilder()
      .setLabel("Change language")
      .setCustomId(`oa_lang-btn_n_${interaction.user.id}`)
      .setStyle(ButtonStyle.Secondary)
      .setDisabled(false)
  );

  rows.push(row2);
  await interaction.editReply({
    embeds: embeds,
    components: rows,
  });
}
