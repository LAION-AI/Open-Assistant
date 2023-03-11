import { Button, Card, CardBody, Flex } from "@chakra-ui/react";
import { List } from "lucide-react";
import { GetServerSideProps } from "next";
import Head from "next/head";
import Link from "next/link";
import { useTranslation } from "next-i18next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { Flags } from "react-feature-flags";
import { ChatConversation } from "src/components/Chat/ChatConversation";
import { getDashboardLayout } from "src/components/Layout";

const Chat = ({ id }: { id: string }) => {
  const { t } = useTranslation(["common", "chat"]);

  return (
    <>
      <Head>
        <title>{t("chat")}</title>
      </Head>

      <Flags authorizedFlags={["chat"]}>
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
      </Flags>
    </>
  );
};

Chat.getLayout = getDashboardLayout;

export const getServerSideProps: GetServerSideProps<{ id: string }, { id: string }> = async ({
  locale = "en",
  params,
}) => ({
  props: {
    id: params.id,
    ...(await serverSideTranslations(locale)),
  },
});

export default Chat;
