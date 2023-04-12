import { Card, CardBody, Divider } from "@chakra-ui/react";
import { FormProvider, useForm } from "react-hook-form";
import { ChatConfigForm } from "src/types/Chat";

import { ChatConfigSummary } from "./ChatConfigSummary";
import { useChatContext } from "./ChatContext";
import { ChatConversation } from "./ChatConversation";
import { InferencePoweredBy } from "./InferencePoweredBy";

export const ChatSection = ({ chatId }: { chatId: string | null }) => {
  const { modelInfos } = useChatContext();

  console.assert(modelInfos.length > 0, "No model config was found");
  const form = useForm<ChatConfigForm>({
    //NOTE: we should at some point validate the cache, in case models were added or deleted
    // or certain parameters disabled
    defaultValues: {
      ...modelInfos[0].parameter_configs[0].sampling_parameters,
      model_config_name: modelInfos[0].name,
    },
  });

  // useCacheChatForm(form);

  return (
    <FormProvider {...form}>
      <Card className="max-w-5xl mx-auto">
        <CardBody display="flex" flexDirection="column" gap="2">
          <ChatConversation chatId={chatId} />
          <ChatConfigSummary />
          <Divider />
          <InferencePoweredBy />
        </CardBody>
      </Card>
    </FormProvider>
  );
};
