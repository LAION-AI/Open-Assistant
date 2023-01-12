import { Box, Grid, GridItem, GridItemProps, Heading, Text, useColorModeValue } from "@chakra-ui/react";
import Head from "next/head";
import { FiChevronDown } from "react-icons/fi";
import { getDashboardLayout } from "src/components/Layout";
import RankItem from "src/components/RankItem";

const Leaderboard = () => {
  const backgroundColor = useColorModeValue("white", "gray.800");

  const GridProps: GridItemProps = {
    justifyContent: "start",
  };
  const filter = [
    {
      title: "User",
      isActive: false,
      GridItemProps: { ...GridProps, justifyContent: "start" },
    },
    {
      title: "Rank",
      isActive: false,
      GridItemProps: { ...GridProps, justifyContent: "center" },
    },
    {
      title: "Score",
      isActive: false,
      GridItemProps: { ...GridProps, justifyContent: "center" },
    },
    {
      title: "Medal",
      isActive: false,
      GridItemProps: { ...GridProps, justifyContent: "center" },
    },
  ];

  return (
    <>
      <Head>
        <title>Leaderboard - Open Assistant</title>
        <meta name="description" content="Leaderboard Rankings" charSet="UTF-8" />
      </Head>
      <Box display="flex" flexDirection="column">
        <Heading fontSize="2xl" fontWeight="bold" pb="4">
          Leaderboard
        </Heading>
        <Grid>
          <GridItem
            colSpan={4}
            bg={backgroundColor}
            display="grid"
            gridTemplateColumns="repeat(4, 1fr)"
            p="4"
            borderRadius="lg"
            mb="4"
            shadow="base"
          >
            {filter.map((item, index) => (
              <GridItem key={index} display="flex" {...item.GridItemProps}>
                <Box display="flex" alignItems="center" gap="2" width="fit-content" borderRadius="md" cursor="pointer">
                  <Text fontSize="sm" fontWeight="bold" textTransform="uppercase">
                    {item.title}
                  </Text>

                  <FiChevronDown size="16" />
                </Box>
              </GridItem>
            ))}
          </GridItem>
        </Grid>
        <Grid templateColumns="repeat(4, 1fr)" bg={backgroundColor} borderRadius="xl" shadow="base" p="4" gap="6">
          <RankItem />
        </Grid>
      </Box>
    </>
  );
};

Leaderboard.getLayout = getDashboardLayout;

export default Leaderboard;
