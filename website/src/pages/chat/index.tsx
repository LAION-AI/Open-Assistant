import { GetServerSideProps, InferGetServerSidePropsType } from "next";
import Head from "next/head";
import { getToken } from "next-auth/jwt";
import { useTranslation } from "next-i18next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import React from "react";
import { ChatListBase } from "src/components/Chat/ChatListBase";
import { getDashboardLayout } from "src/components/Layout";
import { isChatEnable } from "src/lib/isChatEnable";
import { createInferenceClient } from "src/lib/oasst_inference_client";
import { GetChatsResponse } from "src/types/Chat";

type ChatListProps = {
  chatResponse: GetChatsResponse;
};

const ChatList = ({ chatResponse }: InferGetServerSidePropsType<typeof getServerSideProps>) => {
  const { t } = useTranslation(["chat"]);

  return (
    <>
      <Head>
        <title>{t("chat")}</title>
      </Head>
      <ChatListBase chats={chatResponse} isSideBar={false} className="max-w-5xl mx-auto" />
    </>
  );
};

ChatList.getLayout = getDashboardLayout;

export const getServerSideProps: GetServerSideProps<ChatListProps> = async ({ locale = "en", req }) => {
  if (!isChatEnable()) {
    return {
      notFound: true,
    };
  }

  const token = await getToken({ req });
  const client = createInferenceClient(token!);
  const chats = await client.get_my_chats();

  return {
    props: {
      chatResponse: chats,
      ...(await serverSideTranslations(locale)),
    },
  };
};

export default ChatList;
