import { Divider, Flex, Grid, Icon, Text } from "@chakra-ui/react";
import Head from "next/head";
import Link from "next/link";
import { useSession } from "next-auth/react";
import React from "react";
export { getServerSideProps } from "src/lib/defaultServerSideProps";
import { useTranslation } from "next-i18next";
import { SurveyCard } from "src/components/Survey/SurveyCard";

export default function DeleteAccount() {
  const { t } = useTranslation("account");
  const { data: session } = useSession();

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
      <Flex
        as="main"
        direction="column"
        m="auto"
        className="oa-basic-theme max-w-7xl"
        alignContent="center"
        p={6}
        gap={4}
      >
        <SurveyCard className="w-full">
          <Title>{t("delete_account")}</Title>
          <Divider />
        </SurveyCard>
      </Flex>
    </>
  );
}

const Title = ({ children }) => (
  <Text as="b" display="block" fontSize="2xl" py={2}>
    {children}
  </Text>
);
