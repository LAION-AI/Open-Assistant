import { FormProvider, useForm } from "react-hook-form";
import { ChatConfigFormData } from "src/types/Chat";

import { ChatConfig } from "./ChatConfig";
import { ChatProvider } from "./ChatContext";
import { ChatConversation } from "./ChatConversation";
import { useChatInitialData } from "./ChatInitialDataContext";

export const ChatSection = ({ chatId }: { chatId: string | null }) => {
  const { modelInfos } = useChatInitialData();

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
      <ChatProvider>
        <ChatConversation chatId={chatId} key={chatId} getConfigValues={form.getValues} />
        <ChatConfig />
      </ChatProvider>
    </FormProvider>
  );
};
