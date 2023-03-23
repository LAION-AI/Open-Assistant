import { FormProvider, useForm } from "react-hook-form";
import { WorkParametersInput } from "src/types/Chat";

import { ChatConfigDrawer } from "./ChatConfigDrawer";
import { useChatContext } from "./ChatContext";
import { ChatConversation } from "./ChatConversation";

export const ChatSection = ({ chatId }: { chatId: string }) => {
  const { modelInfos } = useChatContext();
  const form = useForm<WorkParametersInput>({
    defaultValues: modelInfos[0].parameter_configs[0].work_parameters,
  });

  return (
    <FormProvider {...form}>
      <ChatConversation chatId={chatId} />
      <ChatConfigDrawer></ChatConfigDrawer>
    </FormProvider>
  );
};
