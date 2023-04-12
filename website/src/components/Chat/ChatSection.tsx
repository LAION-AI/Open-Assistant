import { Card, CardBody, Divider } from "@chakra-ui/react";
import dynamic from "next/dynamic";
import { FormProvider, useForm } from "react-hook-form";
import { useCacheConfig } from "src/hooks/chat/useCacheConfig";
import { ChatConfigFormData } from "src/types/Chat";

import { ChatConfigSaver } from "./ChatConfigSaver";
import { useChatContext } from "./ChatContext";
import { ChatConversation } from "./ChatConversation";
import { InferencePoweredBy } from "./InferencePoweredBy";

const ChatConfigSummary = dynamic(() => import("./ChatConfigSummary"), { ssr: false });

export const ChatSection = ({ chatId }: { chatId: string | null }) => {
  const { modelInfos } = useChatContext();

  console.assert(modelInfos.length > 0, "No model config was found");
  const [config] = useCacheConfig();

  const form = useForm<ChatConfigFormData>({
    defaultValues: config,
  });

  return (
    <FormProvider {...form}>
      <Card className="max-w-5xl mx-auto">
        <CardBody display="flex" flexDirection="column" gap="2">
          <ChatConversation chatId={chatId} key={chatId} />
          <ChatConfigSummary />
          <Divider />
          <InferencePoweredBy />
        </CardBody>
      </Card>
      <ChatConfigSaver />
    </FormProvider>
  );
};
