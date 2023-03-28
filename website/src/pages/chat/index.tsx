import { Box, Button, Divider, Flex, Progress, Text } from "@chakra-ui/react";
import { GetServerSideProps } from "next";
import Head from "next/head";
import Link from "next/link";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { useCallback } from "react";
import { ChatAuth } from "src/components/Chat/ChatAuth";
import { getDashboardLayout } from "src/components/Layout";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { useFetchChatList } from "src/hooks/chat/useFetchChatList";
import { isChatEnabled } from "src/lib/chat_enabled";
import { INFERNCE_TOKEN_KEY } from "src/lib/oasst_inference_auth";
import { OasstInferenceClient } from "src/lib/oasst_inference_client";
import useSWRMutation from "swr/mutation";

export const getServerSideProps: GetServerSideProps = async ({ locale = "en", res, query }) => {
  if (!isChatEnabled()) {
    return {
      notFound: true,
    };
  }

  const accessToken = query.access_token as string;
  const expire = query.exp as string;
  if (accessToken && expire) {
    const maxAge = Math.floor(Number(expire) - Date.now() / 1000);
    res.setHeader("Set-Cookie", `${INFERNCE_TOKEN_KEY}=${accessToken}; Path=/; Max-Age=${maxAge}`);

    return {
      redirect: {
        destination: "/chat",
      },
      props: {
        ...(await serverSideTranslations(locale)),
      },
    };
  }

  return {
    props: {
      ...(await serverSideTranslations(locale)),
    },
  };
};

const Chat = () => {
  const { t } = useTranslation(["common", "chat"]);
  const router = useRouter();

  const { data, isLoading, error } = useFetchChatList();

  const { trigger: newChatTrigger } = useSWRMutation<{ id: string }>("/chat", () => {
    return new OasstInferenceClient().create_chat();
  });

  const createChat = useCallback(async () => {
    const chat = await newChatTrigger();
    router.push(`/chat/${chat!.id}`);
  }, [newChatTrigger, router]);

  return (
    <>
      <Head>
        <title>{t("chat")}</title>
      </Head>
      <Box className="max-w-5xl mx-auto">
        {isLoading && <Progress size="sm" isIndeterminate />}
        {error && <>Error while fetch chats</>}
        {data && (
          <SurveyCard>
            <Flex direction="column" gap="4">
              <Text fontSize="xl" fontWeight="bold">
                {t("chat:your_chats")}
              </Text>
              <Divider />
              {data?.chats.map(({ id, modified_at, title }) => (
                <Link key={id} href={`/chat/${id}`}>
                  <Flex
                    as={Button}
                    bg="inherit"
                    py={2}
                    w="full"
                    borderRadius="sm"
                    gap={6}
                    justifyContent="space-between"
                  >
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
        )}
        <ChatAuth />
      </Box>
    </>
  );
};

Chat.getLayout = getDashboardLayout;

export default Chat;
