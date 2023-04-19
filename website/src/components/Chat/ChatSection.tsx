import { Card, CardBody, Divider } from "@chakra-ui/react";
import dynamic from "next/dynamic";
import { FormProvider, useForm } from "react-hook-form";
import { ChatConfigFormData } from "src/types/Chat";
import { getConfigCache } from "src/utils/chat";

import { ChatConfigSaver } from "./ChatConfigSaver";
import { useChatContext } from "./ChatContext";
import { ChatConversation } from "./ChatConversation";
import { InferencePoweredBy } from "./InferencePoweredBy";

const ChatConfigSummary = dynamic(() => import("./ChatConfigSummary"), { ssr: false });

export const ChatSection = ({ chatId }: { chatId: string | null }) => {
  const { modelInfos } = useChatContext();

  console.assert(modelInfos.length > 0, "No model config was found");

  let defaultValues = getConfigCache();
  if (defaultValues) {
    const model = modelInfos.find((model) => model.name === defaultValues.model_config_name);
    if (!model) {
      defaultValues = null;
    }
  }
  if (!defaultValues) {
    defaultValues = {
      ...modelInfos[0].parameter_configs[0].sampling_parameters,
      model_config_name: modelInfos[0].name,
    };
  }

  const form = useForm<ChatConfigFormData>({ defaultValues });
  return (
    <FormProvider {...form}>
      <Card className="mx-auto" maxW={{ base: "min(64rem, 90vw)", lg: "36rem", xl: "3xl", "2xl": "5xl" }}>
        <CardBody display="flex" flexDirection="column" gap="2">
          <ChatConversation chatId={chatId} key={chatId} getConfigValues={form.getValues} />
          <ChatConfigSummary />
          <Divider />
          <InferencePoweredBy />
        </CardBody>
      </Card>
      <ChatConfigSaver />
    </FormProvider>
  );
};
