import { Button, Progress } from "@chakra-ui/react";
import Head from "next/head";
import { useTranslation } from "next-i18next";
import { useCallback, useMemo } from "react";
import { getDashboardLayout } from "src/components/Layout";
import { post } from "src/lib/api";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";
import { Flags } from "react-feature-flags";
import { ChatConversation } from "src/components/Chat/ChatConversation";
import useSWRMutation from "swr/mutation";

const Chat = () => {
  const { t } = useTranslation("common");
  const {
    trigger: newChatTrigger,
    data: createChatResponse,
    isMutating: isCreatingChat,
  } = useSWRMutation<{ id: string }>("/api/chat", post);

  const createChat = useCallback(() => newChatTrigger(), [newChatTrigger]);

  const content = useMemo(() => {
    if (isCreatingChat) {
      return <Progress size="sm" isIndeterminate />;
    }
    const chatId = createChatResponse?.id;
    if (chatId) {
      return <ChatConversation chatId={chatId} />;
    }
    return <Button onClick={createChat}>{t("create_chat")}</Button>;
  }, [createChat, createChatResponse?.id, isCreatingChat, t]);

  return (
    <>
      <Head>
        <title>{t("chat")}</title>
      </Head>

      <Flags authorizedFlags={["chat"]}>{content}</Flags>
    </>
  );
};

Chat.getLayout = getDashboardLayout;

export default Chat;
