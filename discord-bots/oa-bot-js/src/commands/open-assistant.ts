import { SlashCommandBuilder } from "discord.js";
import { getUserLang } from "../modules/open-assistant/user.js";
import { getTranlation } from "../modules/open-assistant/langs.js";
import {
  langInteraction,
  initInteraction,
} from "../modules/open-assistant/interactions.js";

export default {
  data: new SlashCommandBuilder()
    .setName("open-assistant")
    .setDescription("Help in the data collection of open assistant"),
  async execute(interaction, client, commands, commandType) {
    var lang = await getUserLang(interaction.user.id);
    await interaction.deferReply();

    if (!lang) {
      await langInteraction(interaction);
    } else {
      var translation = await getTranlation(lang);
      await initInteraction(interaction, translation, lang);
      return;
    }
  },
};
