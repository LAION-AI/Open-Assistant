export { getStaticProps } from "src/lib/defaultServerSideProps";
import { Box, Card, CardBody, Grid, Heading, Stack, Text, useColorModeValue } from "@chakra-ui/react";
import Head from "next/head";
import { useTranslation } from "next-i18next";
import React from "react";
import { TeamMember } from "src/components/TeamMember";

import data from "../data/team.json";

const Team = () => {
  const cardBackgroundColor = useColorModeValue("gray.100", "gray.800");
  const { groups, people } = data;
  const { t } = useTranslation();
  return (
    <>
      <Head>
        <title>{`${t("who_are_we")} - Open Assistant`}</title>
        <meta name="description" content="The team behind Open Assistant" />
      </Head>
      <Box p="6" className="oa-basic-theme">
        <Stack className="max-w-6xl mx-auto" spacing="6" mb="6">
          <Heading as="h1" size="xl" color="blue.500">
            {t("who_are_we")}
          </Heading>
          <Text fontWeight="bold">{t("team_message")}</Text>
          <Card bg={cardBackgroundColor}>
            <CardBody display="flex" flexDir="column" gap={6}>
              {groups.map((group) => (
                <React.Fragment key={group.name}>
                  <Heading as="h3" size="md">
                    {group.name}
                  </Heading>
                  <Grid gap="6" gridTemplateColumns="repeat(auto-fit, minmax(300px, 1fr))">
                    {group.members.map((id) => {
                      const info = people[id] ?? {};
                      return <TeamMember {...info} key={id} />;
                    })}
                  </Grid>
                </React.Fragment>
              ))}
            </CardBody>
          </Card>
        </Stack>
      </Box>
    </>
  );
};

export default Team;
