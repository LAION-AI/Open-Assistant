import { Divider, Flex, Grid, Icon, Text } from "@chakra-ui/react";
import Head from "next/head";
import Link from "next/link";
import { useSession } from "next-auth/react";
import React from "react";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";
import { Pencil } from "lucide-react";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { get } from "src/lib/api";
import uswSWRImmutable from "swr/immutable";

export default function Account() {
  const { data: session } = useSession();
  const { data } = uswSWRImmutable("/api/user_stats", get);
  if (!session) {
    return;
  }

  console.log(data);
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
        <Flex m="auto" className="max-w-7xl" alignContent="center">
          <SurveyCard className="w-full">
            <Text as="b" display="block" fontSize="2xl" py={2}>
              Your Account
            </Text>
            <Divider />
            <Grid gridTemplateColumns="repeat(2, max-content)" alignItems="center" gap={6} py={4}>
              <Text as="b">Username</Text>
              <Flex gap={2}>
                {session.user.name ?? "(No username)"}
                <Link href="/account/edit">
                  <Icon boxSize={5} as={Pencil} size="1em" />
                </Link>
              </Flex>
              <Text as="b">Email</Text>
              <Text>{session.user.email ?? "(No Email)"}</Text>
            </Grid>
            <p></p>
          </SurveyCard>
        </Flex>
      </main>
    </>
  );
}
