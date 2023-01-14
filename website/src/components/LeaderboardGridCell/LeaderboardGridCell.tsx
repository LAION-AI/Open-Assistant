import { Avatar, Box, Grid, GridItem, Text, useColorModeValue } from "@chakra-ui/react";
import { FiChevronDown } from "react-icons/fi";
import { get } from "src/lib/api";
import useSWR from "swr";

/**
 * Presents a grid of leaderboard entries with more detailed information.
 */
const LeaderboardGridCell = () => {
  const { data: leaderboardEntries } = useSWR("/api/leaderboard", get);
  const backgroundColor = useColorModeValue("white", "gray.800");
  const columns = `repeat(${FILTER.length}, 1fr)`;

  return (
    <>
      <Grid>
        <GridItem
          colSpan={4}
          bg={backgroundColor}
          display="grid"
          gridTemplateColumns={columns}
          p="4"
          borderRadius="lg"
          mb="4"
          shadow="base"
        >
          {FILTER.map(({ title, GridItemProps }, index) => (
            <GridItem key={index} display="flex" {...GridItemProps}>
              <Box display="flex" alignItems="center" gap="2" width="fit-content" borderRadius="md" cursor="pointer">
                <Text fontSize="sm" fontWeight="bold" textTransform="uppercase">
                  {title}
                </Text>

                <FiChevronDown size="16" />
              </Box>
            </GridItem>
          ))}
        </GridItem>
      </Grid>
      <Grid templateColumns={columns} bg={backgroundColor} borderRadius="xl" shadow="base" p="4" gap="6">
        {leaderboardEntries?.map(({ display_name, ranking, score }, index) => (
          <GridItem key={index} colSpan={4} display="grid" gridTemplateColumns={columns} borderRadius="lg" p="2">
            <GridItem overflow="hidden">
              <Box display="flex" gap="2">
                <Avatar size="xs" />
                <Text>{display_name}</Text>
              </Box>
            </GridItem>
            <GridItem>
              <GridItem display="flex" justifyContent="center">
                <Text>{ranking}</Text>
              </GridItem>
            </GridItem>
            <GridItem display="flex" justifyContent="center">
              <Text>{score}</Text>
            </GridItem>
            {/*
            <GridItem display="flex" justifyContent="center">
              <Text fontSize="xl">{item.medal}</Text>
            </GridItem>
              */}
          </GridItem>
        ))}
      </Grid>
    </>
  );
};

/**
 * Specifies the table headers in the grid.
 */
const FILTER = [
  {
    title: "User",
    isActive: false,
    GridItemProps: { justifyContent: "start" },
  },
  {
    title: "Rank",
    isActive: false,
    GridItemProps: { justifyContent: "center" },
  },
  {
    title: "Score",
    isActive: false,
    GridItemProps: { justifyContent: "center" },
  },
  /*
  {
    title: "Medal",
    isActive: false,
    GridItemProps: { justifyContent: "center" },
  },
   */
];

export { LeaderboardGridCell };
