import Head from "next/head";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import React from "react";
import { ChatListBase } from "src/components/Chat/ChatListBase";
import { DashboardLayout } from "src/components/Layout";
export { getStaticProps } from "src/lib/defaultServerSideProps";
import { useBrowserConfig } from "src/hooks/env/BrowserEnv";

const ChatList = () => {
  const { t } = useTranslation();
  const { BYE } = useBrowserConfig();
  const router = useRouter();

  React.useEffect(() => {
    if (BYE) {
      router.push("/bye");
    }
  }, [router, BYE]);

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
