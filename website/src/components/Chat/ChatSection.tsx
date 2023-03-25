import { FormProvider, useForm } from "react-hook-form";
import { ChatConfigForm } from "src/types/Chat";

import { ChatConfigDrawer } from "./ChatConfigDrawer";
import { useChatContext } from "./ChatContext";
import { ChatConversation } from "./ChatConversation";

export const ChatSection = ({ chatId }: { chatId: string }) => {
  const { modelInfos } = useChatContext();

  console.assert(modelInfos.length > 0, "No model config was found");
  const form = useForm<ChatConfigForm>({
    defaultValues: {
      ...modelInfos[0].parameter_configs[0].sampling_parameters,
      model_config_name: modelInfos[0].name,
    },
  });

  return (
    <FormProvider {...form}>
      <ChatConversation chatId={chatId} />
      <ChatConfigDrawer />
    </FormProvider>
  );
};
