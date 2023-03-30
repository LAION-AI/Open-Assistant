export { getStaticProps } from "src/lib/defaultServerSideProps";
import {
  Avatar,
  Badge,
  Box,
  Card,
  CardBody,
  Flex,
  Grid,
  Heading,
  Stack,
  Text,
  useColorModeValue,
} from "@chakra-ui/react";
import { Github } from "lucide-react";
import Head from "next/head";
import Link from "next/link";
import { useTranslation } from "next-i18next";
import React from "react";

import data from "../data/team.json";

const Team = () => {
  const cardBackgroundColor = useColorModeValue("gray.100", "gray.800");
  const contributorBackgroundColor = useColorModeValue("gray.200", "gray.700");
  const { groups, people } = data;
  const { t } = useTranslation();
  return (
    <>
      <Head>
        <title>{`${t("who_are_we")} - Open Assistant`}</title>
        <meta name="description" content="The team behind Open Assistant" />
      </Head>
      <Box fontFamily="Inter" p="6" className="oa-basic-theme">
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
                      const { name, title, githubURL, imageURL } = info;
                      return (
                        <Flex key={id} gap="1" bg={contributorBackgroundColor} borderRadius="md" p="2">
                          <Avatar src={imageURL} loading="lazy" name={name} />
                          <Box ml="3">
                            <Text fontWeight="bold">
                              {name}
                              {githubURL && (
                                <Badge ml="2" mb="0.5">
                                  <Link href={githubURL} target="_default" rel="noreferrer" title="github">
                                    <Github size={12} />
                                  </Link>
                                </Badge>
                              )}
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
        </Stack>
      </Box>
    </>
  );
};

export default Team;
