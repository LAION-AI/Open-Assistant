import { Box, Button, Divider, Flex, Progress, Text } from "@chakra-ui/react";
import { GetServerSideProps } from "next";
import Head from "next/head";
import Link from "next/link";
import { useRouter } from "next/router";
import { useSession } from "next-auth/react";
import { useTranslation } from "next-i18next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { useCallback, useMemo } from "react";
import { ChatAuth } from "src/components/Chat/ChatAuth";
import { getDashboardLayout } from "src/components/Layout";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { get, post } from "src/lib/api";
import { isChatEnabled } from "src/lib/chat_enabled";
import { GetChatsResponse } from "src/types/Chat";
import useSWR from "swr";
import useSWRMutation from "swr/mutation";

export const getServerSideProps: GetServerSideProps = async ({ locale }) => {
  if (!isChatEnabled()) {
    return {
      notFound: true,
    };
  }
  return {
    props: {
      inferenceHost: process.env.INFERENCE_SERVER_HOST,
      ...(await serverSideTranslations(locale)),
    },
  };
};

const Chat = ({ inferenceHost }: { inferenceHost: string }) => {
  const { t } = useTranslation(["common", "chat"]);
  const router = useRouter();
  const { data: session } = useSession();
  const isAuthenticatedInference = session?.inference.isAuthenticated;

  const { data } = useSWR<GetChatsResponse>(isAuthenticatedInference && "/api/chat", get, { revalidateOnFocus: true });

  const { trigger: newChatTrigger } = useSWRMutation<{ id: string }>("/api/chat", post);

  const createChat = useCallback(async () => {
    const chat = await newChatTrigger();
    router.push(`/chat/${chat!.id}`);
  }, [newChatTrigger, router]);

  const content = useMemo(() => {
    if (!data) {
      return <Progress size="sm" isIndeterminate />;
    }
    return (
      <SurveyCard>
        <Flex direction="column" gap="4">
          <Text fontSize="xl" fontWeight="bold">
            {t("chat:your_chats")}
          </Text>
          <Divider />
          {data.chats.map(({ id, modified_at, title }) => (
            <Link key={id} href={`/chat/${id}`}>
              <Flex as={Button} bg="inherit" py={2} w="full" borderRadius="sm" gap={6} justifyContent="space-between">
                <Text overflowX="hidden" textOverflow="ellipsis">
                  {title ?? t("chat:empty")}
                </Text>
                <Text>
                  {t("chat:chat_date", {
                    val: new Date(modified_at),
                    formatParams: { val: { dateStyle: "short", timeStyle: "short" } },
                  })}
                </Text>
              </Flex>
            </Link>
          ))}
          <Divider />
          <Button maxW="2xs" onClick={createChat}>
            {t("create_chat")}
          </Button>
        </Flex>
      </SurveyCard>
    );
  }, [data, createChat, t]);

  return (
    <>
      <Head>
        <title>{t("chat")}</title>
      </Head>
      <Box className="max-w-5xl mx-auto">
        {content}
        <ChatAuth inferenceHost={inferenceHost} />
      </Box>
    </>
  );
};

Chat.getLayout = getDashboardLayout;

export default Chat;
