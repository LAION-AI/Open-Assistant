import {
  SlashCommandBuilder,
  ActionRowBuilder,
  ButtonStyle,
  ButtonBuilder,
} from "discord.js";
import redis from "../modules/redis.js";
import chatFN from "../modules/chat.js";

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
        .addChoices(
          {
            name: "OA_SFT_Llama_30B",
            value: "OA_SFT_Llama_30B",
          },
          {
            name: "oasst-sft-4-pythia-12b",
            value: "OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5",
          }
        )
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
    if (!model) {
      let userModel = await redis.get(`model_${interaction.user.id}`);
      if (userModel) {
        model = userModel;
      } else {
        model = process.env.OPEN_ASSISTANT_DEFAULT_MODEL || "OA_SFT_Llama_30B";
        redis.set(`model_${interaction.user.id}`, model);
      }
    } else {
      redis.set(`model_${interaction.user.id}`, model);
    }
    if (!preset) preset = "k50";
    // sleep for  30s

    if (model.includes("Llama")) {
      try {
        let chat = await redis.get(`chat_${interaction.user.id}`);
        let chatId = chat ? chat.split("_")[0] : null;
        let parentId = chat ? chat.split("_")[1] : null;
        let { assistant_message, OA } = await chatFN(
          model,
          interaction.user,
          message,
          chatId,
          parentId,
          presets,
          preset
        );
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
            .setCustomId(`vote_${assistant_message.id}_down`),
          new ButtonBuilder()
            .setStyle(ButtonStyle.Secondary)
            .setDisabled(false)
            .setLabel(
              `${model.replaceAll("OpenAssistant/", "").replaceAll("_", "")}`
            )
            .setCustomId(`model_${assistant_message.id}`)
        );
        // using events
        let events = await OA.stream_events({
          chat_id: chatId,
          message_id: assistant_message.id,
        });
        events.on("data", async (c) => {
          /*  let string = JSON.parse(c);
          if (!string.queue_position) {
            await commandType.reply(interaction, {
              content: `${string} <a:loading:1051419341914132554>`,
              components: [],
            });
          }*/
        });
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
    } else {
      let { assistant_message, error } = await chatFN(
        model,
        interaction.user,
        message
      );
      if (error) {
        await commandType.reply(
          interaction,
          `There was an error while executing this command! ${error}`
        );
      }
      const row = new ActionRowBuilder().addComponents(
        new ButtonBuilder()
          .setStyle(ButtonStyle.Secondary)
          .setDisabled(false)
          .setLabel(
            `${model.replaceAll("OpenAssistant/", "").replaceAll("_", "")}`
          )
          .setCustomId(`model_${interaction.user.id}`)
      );
      await commandType.reply(interaction, {
        content: assistant_message,
        components: [row],
      });
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
