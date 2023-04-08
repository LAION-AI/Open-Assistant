import { FormProvider, useForm } from "react-hook-form";
import { getCachedChatForm, useCacheChatForm } from "src/hooks/chat/useCacheConfig";
import { ChatConfigForm } from "src/types/Chat";

import { ChatConfigSummary } from "./ChatConfigSummary";
import { useChatContext } from "./ChatContext";
import { ChatConversation } from "./ChatConversation";

export const ChatSection = ({ chatId }: { chatId: string }) => {
  const { modelInfos } = useChatContext();

  console.assert(modelInfos.length > 0, "No model config was found");
  const form = useForm<ChatConfigForm>({
    //NOTE: we should at some point validate the cache, in case models were added or deleted
    // or certain parameters disabled
    defaultValues: getCachedChatForm() ?? {
      ...modelInfos[0].parameter_configs[0].sampling_parameters,
      model_config_name: modelInfos[0].name,
    },
  });

  useCacheChatForm(form);

  return (
    <FormProvider {...form}>
      <ChatConversation chatId={chatId} />
      <ChatConfigSummary />
    </FormProvider>
  );
};
