import Head from "next/head";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { ChatContextProvider } from "src/components/Chat/ChatContext";
import { ChatSection } from "src/components/Chat/ChatSection";
import { ChatLayout } from "src/components/Layout/ChatLayout";
import { get } from "src/lib/api";
import { ModelInfo, PluginEntry } from "src/types/Chat";
export { getServerSideProps } from "src/lib/defaultServerSideProps";
import useSWRImmutable from "swr/immutable";

const Chat = () => {
  const { query } = useRouter();
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
        <ChatContextProvider modelInfos={modelInfos} plugins={plugins}>
          <ChatSection chatId={id} />
        </ChatContextProvider>
      )}
    </>
  );
};

Chat.getLayout = ChatLayout;

export default Chat;
