import {
  EmbedBuilder,
  ButtonBuilder,
  ButtonStyle,
  ActionRowBuilder,
  ModalBuilder,
  TextInputStyle,
  TextInputBuilder,
} from "discord.js";
import { getUserLang, setUserLang } from "../modules/open-assistant/user.js";
import OpenAssistant from "open-assistant.js";
var oa: OpenAssistant = new OpenAssistant(
  process.env.OA_APIKEY,
  process.env.OA_APIURL
);
import {
  getLocaleDisplayName,
  locales,
  getTranlation,
} from "../modules/open-assistant/langs.js";
import { formatTaskType, submitTask } from "../modules/open-assistant/tasks.js";
import {
  langInteraction,
  taskInteraction,
  initInteraction,
  labelInteraction,
} from "../modules/open-assistant/interactions.js";
import {
  formatLabel,
  getLabel,
  labelText,
  getLabels,
} from "../modules/open-assistant/labels.js";

export default {
  data: {
    customId: "open-assistant",
    description: "Open assistant buttons.",
  },
  async execute(
    interaction,
    client,
    action,
    taskId,
    authorId,
    labelTag,
    labelValue,
    labelFlag
  ) {
    if (!interaction) return;
    var user = {
      id: interaction.user.id,
      display_name: interaction.user.username,
      auth_method: "discord",
    };
    if (action == "info") {
      if (authorId != interaction.user.id) {
        await interaction.reply({
          ephemeral: true,
          content: `${interaction.user}, you can't do this action please use '/open-assistant' to get a task.`,
        });
        return;
      }
      await interaction.deferUpdate();
      var lang = await getUserLang(interaction.user.id);
      if (!lang) {
        await langInteraction(interaction);
      } else {
        var translation = await getTranlation(lang);
        var embed = new EmbedBuilder()
          .setColor("#3a82f7")
          .setTimestamp()
          .setTitle("Open assistant Info")
          .setDescription(
            `Open Assistant is a project organized by LAION and is aimed to be the next ChatGPT but open source making it public of everyone. Now is creating the dataset that you can help to create with this bot. \n\n
            **How it works?**\nClick the button "Grab a task" the first time you click it would ask you to know the language you want to use after that it would show a task you can solve in order to contribute to the dataset. If you don't know what you have to do in that task it would be explained in a short way in the top and you can click the button "what i have to do" to get more information, once you have completed the task you submit it.`
          )
          .setURL("https://open-assistant.io/?ref=turing")
          .setFooter({ text: `${getLocaleDisplayName(lang)}` })
          .setThumbnail("https://open-assistant.io/images/logos/logo.png");
        const row = new ActionRowBuilder().addComponents(
          new ButtonBuilder()
            .setLabel(translation.grab_a_task)
            .setCustomId(`open-assistant_tasks_n_${interaction.user.id}`)
            .setStyle(ButtonStyle.Primary)
            .setDisabled(false),
          new ButtonBuilder()
            .setLabel("Change language")
            .setCustomId(`open-assistant_lang-btn_n_${interaction.user.id}`)
            .setStyle(ButtonStyle.Secondary)
            .setDisabled(false)
        );
        await interaction.editReply({
          embeds: [embed],
          components: [row],
        });
      }
    }
    if (action == "tasks") {
      if (authorId != interaction.user.id) {
        await interaction.reply({
          ephemeral: true,
          content: `${interaction.user}, you can't do this action please use '/open-assistant' to get a task.`,
        });
        return;
      }
      await interaction.deferUpdate();
      var lang = await getUserLang(interaction.user.id);
      if (!lang) {
        await langInteraction(interaction);
      } else {
        var translation = await getTranlation(lang);
        await taskInteraction(interaction, lang, user, translation, client);
      }
    }
    if (action == "lang") {
      if (authorId != interaction.user.id) {
        await interaction.reply({
          ephemeral: true,
          content: `${interaction.user}, you can't do this action please use '/open-assistant' to get a task.`,
        });
        return;
      }
      var selected = interaction.values[0];
      await interaction.deferUpdate();
      await setUserLang(interaction.user.id, selected);
      var translation = await getTranlation(selected);
      var successEmbed = new EmbedBuilder()
        .setColor(`#51F73A`)
        .setTimestamp()
        .setDescription(
          `Language changed to **${getLocaleDisplayName(
            selected
          )} (${selected})**`
        )
        .setURL("https://open-assistant.io/?ref=turing");
      interaction.editReply({
        embeds: [successEmbed],
        components: [],
      });
      setTimeout(async () => {
        await initInteraction(interaction, translation, selected);
      }, 3000);
    }
    if (action == "lang-btn") {
      if (authorId != interaction.user.id) {
        await interaction.reply({
          ephemeral: true,
          content: `${interaction.user}, you can't do this action please use '/open-assistant' to get a task.`,
        });
        return;
      }
      await interaction.deferUpdate();

      await langInteraction(interaction);
    }
    if (action == "skip") {
      if (authorId != interaction.user.id) {
        await interaction.reply({
          ephemeral: true,
          content: `${interaction.user}, you can't do this action please use '/open-assistant' to get a task.`,
        });
        return;
      }
      await interaction.deferUpdate();

      var lang = await getUserLang(interaction.user.id);
      if (!lang) {
        await langInteraction(interaction);
      } else {
        var translation = await getTranlation(lang);
        await oa.rejectTask(taskId, "", user);
        var index = client.tasks.findIndex((x) => x.id == taskId);
        if (index > -1) {
          client.tasks.splice(index, 1);
        }
        await taskInteraction(interaction, lang, user, translation, client);
      }
    }
    if (action == "text-modal") {
      if (authorId != interaction.user.id) {
        await interaction.reply({
          ephemeral: true,
          content: `${interaction.user}, you can't do this action please use '/open-assistant' to get a task.`,
        });
        return;
      }
      var lang = await getUserLang(interaction.user.id);
      if (!lang) {
        await langInteraction(interaction);
      } else {
        var task = client.tasks.find((x) => x.id == taskId);

        if (!task) {
          await interaction.reply({
            ephemeral: true,
            content: `Task not found, please use skip button to get a new task.`,
          });
          return;
        }
        var translation = await getTranlation(lang);
        const promptInput = new TextInputBuilder()
          .setCustomId("modal-input")
          .setMinLength(10)
          .setLabel(translation[formatTaskType(task.type)].label)
          .setPlaceholder(
            translation[formatTaskType(task.type)].response_placeholder
          )
          .setRequired(true)
          // Paragraph means multiple lines of text.
          .setStyle(TextInputStyle.Paragraph);
        const firstActionRow =
          new ActionRowBuilder<TextInputBuilder>().addComponents(promptInput);
        const modal = new ModalBuilder()
          .setCustomId(`open-assistant_modal-review_${taskId}`)
          .setTitle(
            translation[formatTaskType(task.type)].instruction
              ? translation[formatTaskType(task.type)].instruction
              : translation[formatTaskType(task.type)].label
          );
        modal.addComponents(firstActionRow);
        await interaction.showModal(modal);
      }
    }
    if (action == "modal-review") {
      await interaction.deferUpdate();
      var lang = await getUserLang(interaction.user.id);
      if (!lang) {
        await langInteraction(interaction);
      } else {
        var task = client.tasks.find((x) => x.id == taskId);

        if (!task) {
          await interaction.reply({
            ephemeral: true,
            content: `Task not found, please use skip button to get a new task.`,
          });
          return;
        }
        var translation = await getTranlation(lang);
        task.text = interaction.fields.getTextInputValue("modal-input");
        var row = new ActionRowBuilder();
        var readyEmbed = new EmbedBuilder()
          .setColor("#3a82f7")
          .setTimestamp()
          .setFooter({ text: `${getLocaleDisplayName(lang)}` })
          .setTitle(`Are you sure?`)
          .setDescription(`${task.text}`);
        row.addComponents(
          new ButtonBuilder()
            .setCustomId(
              `open-assistant_modal-submit_${taskId}_${interaction.user.id}`
            )
            .setLabel(`Submit`)
            .setStyle(ButtonStyle.Success),
          new ButtonBuilder()
            .setCustomId(
              `open-assistant_text-modal_${taskId}_${interaction.user.id}`
            )
            .setLabel(`Modify`)
            .setStyle(ButtonStyle.Secondary),
          new ButtonBuilder()
            .setCustomId(
              `open-assistant_skip_${task.id}_${interaction.user.id}`
            )
            .setLabel(`${translation.skip} task`)
            .setStyle(ButtonStyle.Danger)
        );
        await interaction.editReply({
          embeds: [readyEmbed],
          components: [row],
        });
        /*  var text = interaction.fields.getTextInputValue("modal-input");
          await submitTask(
            taskId,
            user,
            interaction,
            { text },
            lang,
            task,
            client
          );*/
      }
    }
    if (action == "modal-submit") {
      await interaction.deferUpdate();
      var lang = await getUserLang(interaction.user.id);
      if (!lang) {
        await langInteraction(interaction);
      } else {
        var task = client.tasks.find((x) => x.id == taskId);

        if (!task) {
          await interaction.reply({
            ephemeral: true,
            content: `Task not found, please use skip button to get a new task.`,
          });
          return;
        }
        await submitTask(
          taskId,
          user,
          interaction,
          { text: task.text },
          lang,
          task,
          client
        );
      }
    }
    if (action == "label") {
      if (authorId != interaction.user.id) {
        await interaction.reply({
          ephemeral: true,
          content: `${interaction.user}, you can't do this action please use '/open-assistant' to get a task.`,
        });
        return;
      }
      var lang = await getUserLang(interaction.user.id);
      if (!lang) {
        await interaction.deferUpdate();

        await langInteraction(interaction);
      } else {
        await labelInteraction(
          lang,
          client,
          taskId,
          interaction,
          labelTag,
          labelValue,
          user,
          labelFlag
        );
      }
    }
  },
};
