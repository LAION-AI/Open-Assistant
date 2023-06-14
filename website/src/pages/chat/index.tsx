import Head from "next/head";
import { useTranslation } from "next-i18next";
import React from "react";
import { ChatListBase } from "src/components/Chat/ChatListBase";
import { DashboardLayout } from "src/components/Layout";
export { getStaticProps } from "src/lib/defaultServerSideProps";

const ChatList = () => {
  const { t } = useTranslation();

  return (
    <>
      <Head>
        <title>{t("chat")}</title>
      </Head>
      <ChatListBase
        // TODO: enable this after visually differentiating hidden from visible chats & allowing 'unhide'
        allowViews={process.env.NODE_ENV === "development"}
        className="max-w-5xl mx-auto"
        pt="4"
        px="4"
        borderRadius="xl"
        _light={{
          bg: "white",
        }}
        _dark={{
          bg: "gray.700",
        }}
        shadow="md"
        noScrollbar
      />
    </>
  );
};

ChatList.getLayout = DashboardLayout;

export default ChatList;
