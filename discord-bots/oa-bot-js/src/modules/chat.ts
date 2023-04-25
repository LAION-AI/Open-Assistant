import { createInferenceClient } from "../modules/inference/client.js";
import { HfInference } from "@huggingface/inference";
const hf = new HfInference(process.env.HUGGINGFACE_TOKEN);

export default async function chat(
  model,
  user,
  message,
  chatId?,
  parentId?,
  presets?,
  preset?
) {
  if (model.includes("Llama")) {
    const OA = await createInferenceClient(user.username, user.id);
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
    return { assistant_message, OA };
  } else {
    let result = await huggingface(
      model,
      `<|prompter|>${message}<|endoftext|>\n<|assistant|>`
    );
    if (result.error) {
      return { error: result.error };
    }
    return { assistant_message: result.response };
  }
}

export async function huggingface(model, input) {
  try {
    let oldText;
    let loop = true;
    while (loop) {
      let response = await hf.textGeneration({
        model: model,
        inputs: input,
      });
      let answer = response.generated_text.split("<|assistant|>")[1];
      if (answer == oldText) {
        loop = false;
      } else {
        if (!oldText) {
          oldText = answer;
          input += answer;
        } else {
          oldText += answer;
          input += answer;
        }
      }
    }

    return { response: oldText };
  } catch (err: any) {
    console.log(err);
    return {
      error: err.message,
    };
  }
}
