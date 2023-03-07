import { Button, Divider, Flex, Progress, Text } from "@chakra-ui/react";
import Head from "next/head";
import { useTranslation } from "next-i18next";
import { useCallback, useMemo } from "react";
import { getDashboardLayout } from "src/components/Layout";
import { get, post } from "src/lib/api";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";
import Link from "next/link";
import { useRouter } from "next/router";
import { Flags } from "react-feature-flags";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { GetChatsResponse } from "src/types/Chat";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

const Chat = () => {
  const { t } = useTranslation(["common", "chat"]);
  const router = useRouter();

  const { data } = useSWRImmutable<GetChatsResponse>("/api/chat", get);

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
          {data.chats.map(({ id }) => (
            <Link key={id} href={`/chat/${id}`}>
              {/* TODO: we really only the have the id for each case our users will probably have no idea which is which
               maybe we could show the last message & its date, this is not provided by the API right now */}
              <Text as={Button} py={2} display="block" bg="inherit" w="full" textAlign="start" borderRadius="sm">
                {id}
              </Text>
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

      <Flags authorizedFlags={["chat"]}>{content}</Flags>
    </>
  );
};

Chat.getLayout = getDashboardLayout;

export default Chat;
