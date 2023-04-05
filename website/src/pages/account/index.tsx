import { Box, Divider, Flex, Grid, Icon, Text } from "@chakra-ui/react";
import Head from "next/head";
import Link from "next/link";
import { useSession } from "next-auth/react";
import React from "react";
export { getStaticProps } from "src/lib/defaultServerSideProps";
import { Pencil } from "lucide-react";
import { useTranslation } from "next-i18next";
import { XPBar } from "src/components/Account/XPBar";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { get } from "src/lib/api";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { LeaderboardEntity, LeaderboardTimeFrame } from "src/types/Leaderboard";
import uswSWRImmutable from "swr/immutable";

export default function Account() {
  const { t } = useTranslation("leaderboard");
  const { data: session } = useSession();
  const { data: entries } = uswSWRImmutable<Partial<{ [time in LeaderboardTimeFrame]: LeaderboardEntity }>>(
    "/api/user_stats",
    get,
    {
      fallbackData: {},
    }
  );
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
      <main className="oa-basic-theme p-6">
        <Flex direction="column" m="auto" className="max-w-7xl" alignContent="center" gap={4}>
          <SurveyCard className="w-full">
            <Title>{t("your_account")}</Title>
            <Divider />
            <Grid gridTemplateColumns="repeat(2, max-content)" alignItems="center" gap={6} py={4}>
              <Text as="b">{t("username")}</Text>
              <Flex gap={2}>
                {session.user.name ?? t("no_username")}
                <Link href="/account/edit">
                  <Icon boxSize={5} as={Pencil} size="1em" />
                </Link>
              </Flex>
              <Text as="b">Email</Text>
              <Text>{session.user.email ?? t("no_email")}</Text>
            </Grid>
            <Divider my={4} />
            <XPBar />
          </SurveyCard>
          <SurveyCard>
            <Title>{t("your_stats")}</Title>
            {[
              LeaderboardTimeFrame.day,
              LeaderboardTimeFrame.week,
              LeaderboardTimeFrame.month,
              LeaderboardTimeFrame.total,
            ]
              .map((key) => ({ key, values: entries[key] }))
              .filter(({ values }) => values)
              .map(({ key, values }) => (
                <Box key={key} py={4}>
                  <Title>{t(getTypeSafei18nKey(key))}</Title>
                  <Flex w="full" wrap="wrap" alignItems="flex-start" gap={4}>
                    <TableColumn>
                      <Entry title={t("score")} value={values.leader_score} />
                      <Entry title={t("rank")} value={values.rank} />
                      <Entry title={t("prompt")} value={values.prompts} />
                      <Entry title={t("accepted_prompts")} value={values.accepted_prompts} />
                    </TableColumn>
                    <TableColumn>
                      <Entry title={t("replies_assistant")} value={values.replies_assistant} />
                      <Entry title={t("accepted")} value={values.accepted_replies_assistant} />
                      <Entry title={t("replies_prompter")} value={values.replies_prompter} />
                      <Entry title={t("accepted")} value={values.accepted_replies_prompter} />
                    </TableColumn>
                    <TableColumn>
                      <Entry title={t("labels_full")} value={values.labels_full} />
                      <Entry title={t("labels_simple")} value={values.labels_simple} />
                      <Entry title={t("rankings")} value={values.rankings_total} />
                      <Entry title={t("reply_ranked_1")} value={values.reply_ranked_1} />
                    </TableColumn>
                  </Flex>
                </Box>
              ))}
          </SurveyCard>
        </Flex>
      </main>
    </>
  );
}

const Title = ({ children }) => (
  <Text as="b" display="block" fontSize="2xl" py={2}>
    {children}
  </Text>
);

const TableColumn = ({ children }) => {
  return (
    <Grid gridTemplateColumns="1fr max-content" mx={8} w="60" gap={2}>
      {children}
    </Grid>
  );
};

const Entry = ({ title, value }) => {
  return (
    <>
      <span className="text-start">{title}</span>
      <span className="text-end">{value}</span>
    </>
  );
};
