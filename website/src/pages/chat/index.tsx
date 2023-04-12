import { GetServerSideProps, InferGetServerSidePropsType } from "next";
import Head from "next/head";
import { getToken } from "next-auth/jwt";
import { useTranslation } from "next-i18next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import React from "react";
import { ChatContextProvider } from "src/components/Chat/ChatContext";
import { ChatSection } from "src/components/Chat/ChatSection";
import { getChatLayout } from "src/components/Layout/ChatLayout";
import { isChatEnable } from "src/lib/isChatEnable";
import { createInferenceClient } from "src/lib/oasst_inference_client";
import { ModelInfo } from "src/types/Chat";

type ChatListProps = {
  modelInfos: ModelInfo[];
};

const ChatList = ({ modelInfos }: InferGetServerSidePropsType<typeof getServerSideProps>) => {
  const { t } = useTranslation(["chat"]);

  return (
    <>
      <Head>
        <title>{t("chat")}</title>
      </Head>
      <ChatContextProvider modelInfos={modelInfos}>
        <ChatSection chatId={null} />
      </ChatContextProvider>
    </>
  );
};

ChatList.getLayout = getChatLayout;

export const getServerSideProps: GetServerSideProps<ChatListProps> = async ({ locale = "en", req }) => {
  if (!isChatEnable()) {
    return {
      notFound: true,
    };
  }

  const token = await getToken({ req });
  const client = createInferenceClient(token!);
  const modelInfos = await client.get_models();

  return {
    props: {
      modelInfos,
      ...(await serverSideTranslations(locale)),
    },
  };
};

export default ChatList;
