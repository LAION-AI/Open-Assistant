import Head from "next/head";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { ChatInitialDataProvider } from "src/components/Chat/ChatInitialDataContext";
import { ChatSection } from "src/components/Chat/ChatSection";
import { ChatLayout } from "src/components/Layout/ChatLayout";
import { get } from "src/lib/api";
import { ModelInfo, PluginEntry } from "src/types/Chat";
export { getServerSideProps } from "src/lib/defaultServerSideProps";
import useSWRImmutable from "swr/immutable";

const Chat = () => {
  const router = useRouter();
  const { query } = router;
  const id = query.id as string;
  const { t } = useTranslation(["common", "chat"]);
  const { data: modelInfos } = useSWRImmutable<ModelInfo[]>("/api/chat/models", get, {
    keepPreviousData: true,
  });
  const { data: plugins } = useSWRImmutable<PluginEntry[]>("/api/chat/plugins", get, {
    keepPreviousData: true,
  });

  return (
    <>
      <Head>
        <title>{t("chat")}</title>
      </Head>
      {modelInfos && plugins && (
        <ChatInitialDataProvider modelInfos={modelInfos} builtInPlugins={plugins}>
          <ChatSection chatId={id} />
        </ChatInitialDataProvider>
      )}
    </>
  );
};

Chat.getLayout = ChatLayout;

export default Chat;
