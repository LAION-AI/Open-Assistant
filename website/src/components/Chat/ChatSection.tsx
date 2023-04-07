import { useEffect } from "react";
import { FormProvider, useForm } from "react-hook-form";
import { ChatConfigForm } from "src/types/Chat";

import { ChatConfigSummary } from "./ChatConfigSummary";
import { useChatContext } from "./ChatContext";
import { ChatConversation } from "./ChatConversation";

const CHAT_CONFIG_KEY = "CHAT_CONFIG";

export const ChatSection = ({ chatId }: { chatId: string }) => {
  const { modelInfos } = useChatContext();

  const oldConfig = localStorage.getItem(CHAT_CONFIG_KEY);
  console.assert(modelInfos.length > 0, "No model config was found");
  const form = useForm<ChatConfigForm>({
    //NOTE: we should at some point validate the config, in case models were added or deleted
    // or certain parameters disabled
    defaultValues: oldConfig
      ? JSON.parse(oldConfig)
      : {
          ...modelInfos[0].parameter_configs[0].sampling_parameters,
          model_config_name: modelInfos[0].name,
        },
  });

  const config = form.watch();

  useEffect(() => {
    localStorage.setItem(CHAT_CONFIG_KEY, JSON.stringify(config));
  }, [config]);

  return (
    <FormProvider {...form}>
      <ChatConversation chatId={chatId} />
      <ChatConfigSummary />
    </FormProvider>
  );
};
