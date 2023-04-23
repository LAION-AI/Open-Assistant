import { FormProvider, useForm } from "react-hook-form";
import { ChatConfigFormData } from "src/types/Chat";
import { getConfigCache } from "src/utils/chat";
import { useIsomorphicLayoutEffect } from "usehooks-ts";

import { ChatConfigDesktop } from "./ChatConfigDesktop";
import { ChatConfigSaver } from "./ChatConfigSaver";
import { useChatContext } from "./ChatContext";
import { ChatConversation } from "./ChatConversation";
import { InferencePoweredBy } from "./InferencePoweredBy";
import { ChatWarning } from "./ChatWarning";

const ChatConfigSummary = dynamic(() => import("./ChatConfigSummary"), { ssr: false });

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
      form.reset(cache);
    }
  }, [form.reset, modelInfos]);

  return (
    <FormProvider {...form}>
      <Card className="mx-auto" maxW={{ base: "min(64rem, 90vw)", lg: "36rem", xl: "3xl", "2xl": "5xl" }}>
        <CardBody display="flex" flexDirection="column" gap="2">
          <ChatConversation chatId={chatId} key={chatId} getConfigValues={form.getValues} />
          <ChatConfigSummary />
          <Divider />
          <ChatWarning />
          <InferencePoweredBy />
        </CardBody>
      </Card>
      <ChatConversation chatId={chatId} key={chatId} getConfigValues={form.getValues} />
      <ChatConfigDesktop></ChatConfigDesktop>
      <ChatConfigSaver />
    </FormProvider>
  );
};
