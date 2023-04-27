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
import { ModelInfo } from "src/types/Chat";

interface ChatProps {
  id: string;
  modelInfos: ModelInfo[];
}

const Chat = ({ id, modelInfos }: ChatProps) => {
  const { t } = useTranslation(["common", "chat"]);

  return (
    <>
      <Head>
        <title>{t("chat")}</title>
      </Head>

      <ChatContextProvider modelInfos={modelInfos}>
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
}) => {
  if (!boolean(process.env.ENABLE_CHAT)) {
    return {
      notFound: true,
    };
  }

  const token = await getToken({ req });
  const client = createInferenceClient(token!);
  const modelInfos = await client.get_models();

  return {
    props: {
      id: params!.id,
      modelInfos,
      ...(await serverSideTranslations(locale)),
    },
  };
};

export default Chat;
