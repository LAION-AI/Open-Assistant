import { Button, Card, CardBody, Flex } from "@chakra-ui/react";
import axios from "axios";
import { List } from "lucide-react";
import { GetServerSideProps, InferGetServerSidePropsType } from "next";
import Head from "next/head";
import Link from "next/link";
import { useTranslation } from "next-i18next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { Flags } from "react-feature-flags";
import { ChatSection } from "src/components/Chat/ChatSection";
import { getDashboardLayout } from "src/components/Layout";
import { ModelInfo } from "src/types/Chat";

const Chat = ({ id }: InferGetServerSidePropsType<typeof getServerSideProps>) => {
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
              <ChatSection chatId={id} />
            </Flex>
          </CardBody>
        </Card>
      </Flags>
    </>
  );
};

Chat.getLayout = getDashboardLayout;

export const getServerSideProps: GetServerSideProps<{ id: string; modelInfos: ModelInfo[] }, { id: string }> = async ({
  locale = "en",
  params,
}) => {
  const modelInfos = await axios.get<ModelInfo[]>("/configs/models", {
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
