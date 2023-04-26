import { FormProvider, useForm } from "react-hook-form";
import { ChatConfigFormData } from "src/types/Chat";
import { getConfigCache } from "src/utils/chat";
import { useIsomorphicLayoutEffect } from "usehooks-ts";

import { ChatConfigDesktop } from "./ChatConfigDesktop";
import { ChatConfigSaver } from "./ChatConfigSaver";
import { useChatContext } from "./ChatContext";
import { ChatConversation } from "./ChatConversation";

export const ChatSection = ({ chatId }: { chatId: string | null }) => {
  const { modelInfos } = useChatContext();

  console.assert(modelInfos.length > 0, "No model config was found");

  const form = useForm<ChatConfigFormData>({
    defaultValues: {
      ...modelInfos[0].parameter_configs[0].sampling_parameters,
      model_config_name: modelInfos[0].name,
    },
  });

  useIsomorphicLayoutEffect(() => {
    const cache = getConfigCache();
    const model = modelInfos.find((model) => model.name === cache?.model_config_name);
    if (model && cache) {
      console.log(`resseting form`);
      form.reset(cache);
    }
  }, [form.reset, modelInfos]);

  return (
    <FormProvider {...form}>
      <ChatConversation chatId={chatId} key={chatId} getConfigValues={form.getValues} />

      <ChatConfigDesktop></ChatConfigDesktop>
      <ChatConfigSaver />
    </FormProvider>
  );
};
