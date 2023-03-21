import { Button, Card, CardBody, Flex } from "@chakra-ui/react";
import axios from "axios";
import { List } from "lucide-react";
import { GetServerSideProps } from "next";
import Head from "next/head";
import Link from "next/link";
import { useTranslation } from "next-i18next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { ChatContextProvider } from "src/components/Chat/ChatContext";
import { ChatSection } from "src/components/Chat/ChatSection";
import { getDashboardLayout } from "src/components/Layout";
import { isChatEnabled } from "src/lib/chat_enabled";
import { ModelInfo } from "src/types/Chat";

interface ChatProps {
  id: string;
  modelInfos: ModelInfo[];
}

const Chat = ({ id, modelInfos }: ChatProps) => {
  const { t } = useTranslation(["common", "chat"]);

  return (
    <>
      <Head>
        <title>{t("chat")}</title>
      </Head>

      <ChatContextProvider modelInfos={modelInfos}>
        <Card>
          <CardBody>
            <Flex direction="column" gap="2">
              <Link href="/chat">
                <Button leftIcon={<List />} size="lg">
                  {t("chat:back_to_chat_list")}
                </Button>
              </Link>

              <ChatSection chatId={id}></ChatSection>
            </Flex>
          </CardBody>
        </Card>
      </ChatContextProvider>
    </>
  );
};

Chat.getLayout = getDashboardLayout;

export const getServerSideProps: GetServerSideProps<ChatProps, { id: string }> = async ({ locale = "en", params }) => {
  if (!isChatEnabled()) {
    return {
      notFound: true,
    };
  }

  const { data: modelInfos } = await axios.get<ModelInfo[]>("/configs/models", {
    baseURL: process.env.INFERENCE_SERVER_HOST,
  });

  return {
    props: {
      id: params!.id,
      modelInfos,
      ...(await serverSideTranslations(locale)),
    },
  };
};

export default Chat;
