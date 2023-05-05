import { FormProvider, useForm } from "react-hook-form";
import { ChatConfigFormData } from "src/types/Chat";

import { ChatConfigDesktop } from "./ChatConfigDesktop";
import { useChatContext } from "./ChatContext";
import { ChatConversation } from "./ChatConversation";
import { ChatPluginContextProvider } from "./ChatPluginContext";

export const ChatSection = ({ chatId }: { chatId: string | null }) => {
  const { modelInfos } = useChatContext();

  console.assert(modelInfos.length > 0, "No model config was found");

  const form = useForm<ChatConfigFormData>({
    defaultValues: {
      ...modelInfos[0].parameter_configs[0].sampling_parameters,
      model_config_name: modelInfos[0].name,
      plugins: [],
    },
  });

  return (
    <FormProvider {...form}>
      <ChatPluginContextProvider>
        <ChatConversation chatId={chatId} key={chatId} getConfigValues={form.getValues} />
        <ChatConfigDesktop />
      </ChatPluginContextProvider>
      {/* <ChatConfigSaver /> */}
    </FormProvider>
  );
};
