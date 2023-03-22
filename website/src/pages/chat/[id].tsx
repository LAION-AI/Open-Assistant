import { Button, Card, CardBody, Flex } from "@chakra-ui/react";
import { List } from "lucide-react";
import { GetServerSideProps } from "next";
import Head from "next/head";
import Link from "next/link";
import { useTranslation } from "next-i18next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { ChatConversation } from "src/components/Chat/ChatConversation";
import { getDashboardLayout } from "src/components/Layout";
import { isChatEnabled } from "src/lib/chat_enabled";

interface ChatProps {
  id: string;
}

const Chat = ({ id }: ChatProps) => {
  const { t } = useTranslation(["common", "chat"]);

  return (
    <>
      <Head>
        <title>{t("chat")}</title>
      </Head>

      <Card>
        <CardBody>
          <Flex direction="column" gap="2">
            <Link href="/chat">
              <Button leftIcon={<List />} size="lg">
                {t("chat:back_to_chat_list")}
              </Button>
            </Link>

            <ChatConversation chatId={id} />
          </Flex>
        </CardBody>
      </Card>
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
  return {
    props: {
      id: params.id,
      ...(await serverSideTranslations(locale)),
    },
  };
};

export default Chat;
