import { FormProvider, useForm } from "react-hook-form";
import { ChatConfigFormData } from "src/types/Chat";

import { ChatConfigDesktop } from "./ChatConfigDesktop";
import { ChatConfigForm } from "./ChatConfigForm";
import { useChatContext } from "./ChatContext";
import { ChatConversation } from "./ChatConversation";

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

  const chatConfigForm = <ChatConfigForm />;

  return (
    <FormProvider {...form}>
      <ChatConversation chatId={chatId} key={chatId} getConfigValues={form.getValues} />
      <ChatConfigDesktop>{chatConfigForm}</ChatConfigDesktop>
      {/* <ChatConfigSaver /> */}
    </FormProvider>
  );
};
