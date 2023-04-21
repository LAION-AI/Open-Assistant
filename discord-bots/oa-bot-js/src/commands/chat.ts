import {
  SlashCommandBuilder,
  ActionRowBuilder,
  ButtonStyle,
  ButtonBuilder,
} from "discord.js";
import { createInferenceClient } from "../modules/inference/client.js";
import redis from "../modules/redis.js";

export default {
  disablePing: null,
  data: new SlashCommandBuilder()
    .setName("chat")
    .setDescription("Chat with an Open Assistant AI.")
    .addStringOption((option) =>
      option
        .setName("message")
        .setDescription("The message for the AI")
        .setRequired(true)
    )
    .addStringOption((option) =>
      option
        .setName("model")
        .setDescription("The model you want to use for the AI.")
        .setRequired(false)
        .addChoices({
          name: "OA_SFT_Llama_30B",
          value: "OA_SFT_Llama_30B",
        })
    )
    .addStringOption((option) =>
      option
        .setName("preset")
        .setDescription("The preset you want to use for the AI.")
        .setRequired(false)
        .addChoices(
          {
            name: "k50 (default)",
            value: "k50",
          },
          {
            name: "nucleus9",
            value: "nucleus9",
          },
          {
            name: "typical2",
            value: "typical2",
          },
          {
            name: "typical3",
            value: "typical3",
          }
        )
    ),
  async execute(interaction, client, commands, commandType, options) {
    var message;
    var model;
    var preset;
    await commandType.load(interaction);
    if (!interaction.options) {
      message = options.message;
      model = options.model;
      preset = options.preset;
    } else {
      message = interaction.options.getString("message");
      if (
        message.includes("@everyone") ||
        message.includes("<@") ||
        message.includes("@here")
      ) {
        return;
      }
      model = interaction.options.getString("model");
      preset = interaction.options.getString("preset");
    }
    if (!model)
      model = process.env.OPEN_ASSISTANT_DEFAULT_MODEL || "OA_SFT_Llama_30B";
    if (!preset) preset = "k50";
    // sleep for  30s

    const OA = await createInferenceClient(
      interaction.user.username,
      interaction.user.id
    );

    try {
      let chat = await redis.get(`chat_${interaction.user.id}`);
      let chatId = chat ? chat.split("_")[0] : null;
      let parentId = chat ? chat.split("_")[1] : null;
      if (!chatId) {
        let chat = await OA.create_chat();
        chatId = chat.id;
      }
      let prompter_message = await OA.post_prompter_message({
        chat_id: chatId,
        content: message,
        parent_id: parentId,
      });

      let assistant_message = await OA.post_assistant_message({
        chat_id: chatId,
        model_config_name: model,
        parent_id: prompter_message.id,
        sampling_parameters: presets[preset],
      });
      await redis.set(
        `chat_${interaction.user.id}`,
        `${chatId}_${assistant_message.id}`
      );

      const row = new ActionRowBuilder().addComponents(
        new ButtonBuilder()
          .setStyle(ButtonStyle.Secondary)
          .setLabel(`👍`)
          .setCustomId(`vote_${assistant_message.id}_up`),
        new ButtonBuilder()
          .setStyle(ButtonStyle.Secondary)
          .setLabel(`👎`)
          .setCustomId(`vote_${assistant_message.id}_down`)
      );
      // using events
      let events = await OA.stream_events({
        chat_id: chatId,
        message_id: assistant_message.id,
      });
      events.on("data", async (c) => {});
      events.on("end", async (c) => {
        let msg = await OA.get_message(chatId, assistant_message.id);
        await commandType.reply(interaction, {
          content: msg.content,
          components: [row],
        });
      });
    } catch (err: any) {
      console.log(err);
      // get details of the error
      await commandType.reply(
        interaction,
        `There was an error while executing this command! ${err.message}`
      );
    }
  },
};

const sleep = (milliseconds) => {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
};

let presets = {
  k50: {
    max_new_tokens: 1024,
    temperature: 1,
    repetition_penalty: 1.2,
    top_k: 50,
    top_p: 0.95,
    typical_p: null,
  },
  nucleus9: {
    max_new_tokens: 1024,
    temperature: 0.8,
    top_k: null,
    top_p: 0.9,
    repetition_penalty: 1.2,
    typical_p: null,
  },
  typical2: {
    max_new_tokens: 1024,
    temperature: 0.8,
    top_k: null,
    top_p: null,
    repetition_penalty: 1.2,
    typical_p: 0.2,
  },
  typical3: {
    max_new_tokens: 1024,
    temperature: 0.8,
    top_k: null,
    top_p: null,
    repetition_penalty: 1.2,
    typical_p: 0.3,
  },
};
