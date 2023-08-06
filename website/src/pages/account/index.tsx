import { Divider, Flex, Grid, Icon, Text, Button } from "@chakra-ui/react";
import Head from "next/head";
import Link from "next/link";
import { useSession } from "next-auth/react";
import React, { Fragment } from "react";
export { getStaticProps } from "src/lib/defaultServerSideProps";
import { Discord, Google } from "@icons-pack/react-simple-icons";
import { Pencil } from "lucide-react";
import { useTranslation } from "next-i18next";
import { UserStats } from "src/components/Account/UserStats";
import { XPBar } from "src/components/Account/XPBar";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { get } from "src/lib/api";
import { ExternalProvider, UserAccountResponse } from "src/types/Account";
import { LeaderboardEntity, LeaderboardTimeFrame } from "src/types/Leaderboard";
import useSWRImmutable from "swr/immutable";

export default function Account() {
  const { t } = useTranslation(["leaderboard", "account"]);
  const { data: session } = useSession();
  const { data: userAccounts } = useSWRImmutable<UserAccountResponse>("/api/account", get, { keepPreviousData: true });
  const { data: stats } = useSWRImmutable<Partial<{ [time in LeaderboardTimeFrame]: LeaderboardEntity }>>(
    "/api/user_stats",
    get,
    {
      fallbackData: {},
    }
  );

  if (!session || !userAccounts) {
    return;
  }

  const { emailIsVerified, accounts } = userAccounts;

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
              {accounts.length > 0 && (
                <>
                  <Text as="b" className="col-span-2">
                    {t("account:linked_accounts")}
                  </Text>
                  {accounts.map(({ provider, providerAccountId }) => (
                    <Fragment key={provider + providerAccountId}>
                      <ProviderIcon provider={provider} />
                      <Text>{providerAccountId}</Text>
                    </Fragment>
                  ))}
                </>
              )}
            </Grid>
            <Button as={Link} href="/account/paperack">
              {t("account:edit_paper_ack")}
            </Button>
            <Divider my={4} />
            <XPBar />
          </SurveyCard>
          <UserStats stats={stats} />
          <SurveyCard className="w-full" color="red">
            <Link href="/account/delete">{t("account:delete_account")}</Link>
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

const ProviderIcon = ({ provider }: { provider: ExternalProvider }): JSX.Element => {
  if (provider === "discord") {
    return <Discord />;
  }
  if (provider === "google") {
    return <Google />;
  }
  return <div>❌</div>;
};
