import { boolean } from "boolean";
import { GetServerSideProps } from "next";
import Head from "next/head";
import { getToken } from "next-auth/jwt";
import { useTranslation } from "next-i18next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { ChatContextProvider } from "src/components/Chat/ChatContext";
import { ChatSection } from "src/components/Chat/ChatSection";
import { getChatLayout } from "src/components/Layout/ChatLayout";
import { createInferenceClient } from "src/lib/oasst_inference_client";
import { InferenceMessage, ModelInfo } from "src/types/Chat";
import { ModelInfo, PluginEntry } from "src/types/Chat";

interface ChatProps {
  id: string;
  modelInfos: ModelInfo[];
  messages: InferenceMessage[];
  plugins: PluginEntry[];
}

const Chat = ({ id, modelInfos, messages, plugins }: ChatProps) => {
  const { t } = useTranslation(["common", "chat"]);

  return (
    <>
      <Head>
        <title>{t("chat")}</title>
      </Head>

      <ChatContextProvider modelInfos={modelInfos} messages={messages} plugins={plugins}>
        <ChatSection chatId={id} />
      </ChatContextProvider>
    </>
  );
};

Chat.getLayout = getChatLayout;

export const getServerSideProps: GetServerSideProps<ChatProps, { id: string }> = async ({
  locale = "en",
  params,
  req,
  query,
}) => {
  if (!boolean(process.env.ENABLE_CHAT)) {
    return {
      notFound: true,
    };
  }

  const token = await getToken({ req });
  const client = createInferenceClient(token!);
  const [modelInfos, chat, plugins] = await Promise.all([
    client.get_models(),
    client.get_chat(query.id as string),
    client.get_plugins(),
  ]);

  return {
    props: {
      id: params!.id,
      modelInfos,
      messages: chat.messages.sort((a, b) => Date.parse(a.created_at) - Date.parse(b.created_at)),
      plugins,
      ...(await serverSideTranslations(locale)),
    },
  };
};

export default Chat;
