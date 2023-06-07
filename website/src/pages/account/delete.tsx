import { Button, Divider, Flex, Grid, Icon, ListItem, Text, UnorderedList } from "@chakra-ui/react";
import Head from "next/head";
import Link from "next/link";
import React, { useCallback } from "react";
export { getStaticProps } from "src/lib/defaultServerSideProps";
import { useRouter } from "next/router";
import { signOut, useSession } from "next-auth/react";
import { useTranslation } from "next-i18next";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { del } from "src/lib/api";
import useSWRMutation from "swr/mutation";

export default function DeleteAccount() {
  const { t } = useTranslation("account");
  const { data: session } = useSession();
  const router = useRouter();

  const { trigger } = useSWRMutation("/api/account/delete", del);

  const executeDelete = useCallback(async () => {
    try {
      await trigger();
      signOut({ callbackUrl: "/" });
    } catch (err) {
      console.error(err);
    }
  }, [trigger]);

  if (!session) {
    return;
  }

  return (
    <>
      <Head>
        <title>Open Assistant</title>
        <meta
          name="description"
          content="Conversational AI for everyone. An open source project to create a chat enabled GPT LLM run by LAION and contributors around the world."
        />
      </Head>
      <SurveyCard
        display="flex"
        flexDirection="column"
        mx="auto"
        my={6}
        className="oa-basic-theme max-w-7xl w-full"
        alignContent="center"
        p={6}
        gap={4}
      >
        <Title>{t("delete_account")}</Title>
        <Divider />
        <Text>{t("delete_account_intro")}</Text>
        <UnorderedList>
          <ListItem>{t("delete_account_data")}</ListItem>
          <ListItem>{t("delete_account_leaderboard")}</ListItem>
        </UnorderedList>
        <Text color="red">{t("delete_account_permanent")}</Text>
        <Flex justifyContent="space-evenly">
          <Button colorScheme="blue" onClick={() => router.push("/dashboard")}>
            {t("go_to_dashboard")}
          </Button>
          <Button colorScheme="red" onClick={executeDelete}>
            {t("yes_delete")}
          </Button>
        </Flex>
      </SurveyCard>
    </>
  );
}

const Title = ({ children }) => (
  <Text as="b" display="block" fontSize="2xl" py={2}>
    {children}
  </Text>
);
