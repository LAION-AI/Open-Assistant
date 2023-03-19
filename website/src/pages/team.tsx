export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";
import { Avatar, Badge, Box, Card, CardBody, Flex, Grid, Heading, Text } from "@chakra-ui/react";
import { Github } from "lucide-react";
import Head from "next/head";
import { useTranslation } from "next-i18next";
import Link from "next/link";
import React from "react";
import { getTransparentHeaderLayout } from "src/components/Layout";

import data from "../data/team.json";

const Team = () => {
  const { groups, people } = data;
  const { t } = useTranslation();
  return (
    <>
      <Head>
        <title>{t("who_are_we")} - Open Assistant</title>
        <meta name="description" content="The team begind Open Assistant" />
      </Head>
      <Box fontFamily="Inter" p="6" className="oa-basic-theme">
        <Box className="max-w-6xl mx-auto">
          <Card>
            <CardBody display="flex" flexDirection={"column"} gap={6}>
              <Heading as="h1" size="xl">
                {t("who_are_we")}
              </Heading>
              <Text>{t("team_message")}</Text>
              {groups.map((group) => (
                <React.Fragment key={group.name}>
                  <Text as="h2" fontWeight="bold" size="lg">
                    {group.name}
                  </Text>
                  <Grid gap={6} gridTemplateColumns="repeat(auto-fit, minmax(300px, 1fr))">
                    {group.members.map((id) => {
                      const info = people[id] ?? {};
                      const { name, title, githubURL, imageURL } = info;
                      return (
                        <Flex key={id} gap={2}>
                          <Avatar src={imageURL} loading="lazy" />
                          <Box ml="3">
                            <Text fontWeight="bold">
                              {name}
                              <Badge ml="1">
                                <Link href={githubURL} target="_default" rel="noreferrer" title="github">
                                  <Github size={12} />
                                </Link>
                              </Badge>
                            </Text>
                            <Text fontSize="sm">{title}</Text>
                          </Box>
                        </Flex>
                      );
                    })}
                  </Grid>
                </React.Fragment>
              ))}
            </CardBody>
          </Card>
        </Box>
      </Box>
    </>
  );
};

Team.getLayout = getTransparentHeaderLayout;

export default Team;
