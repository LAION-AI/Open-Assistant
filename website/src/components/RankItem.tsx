import { Avatar, Box, GridItem, Text } from "@chakra-ui/react";

const RankItem = () => {
  const leaderInfo = [
    {
      username: "fozziethebeat",
      rank: 1,
      score: 530,
      medal: "\uD83E\uDD47",
    },
    {
      username: "k_nearest",
      rank: 2,
      score: 420,
      medal: "\uD83E\uDD48",
    },
    {
      username: "zu",
      rank: 3,
      score: 160,
      medal: "\uD83E\uDD49",
    },
    {
      username: "Abd",
      rank: 4,
      score: 140,
      medal: "",
    },
  ];

  return (
    <>
      {leaderInfo.map((item, index) => (
        <GridItem key={index} colSpan={4} display="grid" gridTemplateColumns="repeat(4, 1fr)" borderRadius="lg" p="2">
          <GridItem overflow="hidden">
            <Box display="flex" gap="2">
              <Avatar size="xs" />
              <Text>{item.username}</Text>
            </Box>
          </GridItem>
          <GridItem>
            <GridItem display="flex" justifyContent="center">
              <Text>{item.rank}</Text>
            </GridItem>
          </GridItem>
          <GridItem display="flex" justifyContent="center">
            <Text>{item.score}</Text>
          </GridItem>
          <GridItem display="flex" justifyContent="center">
            <Text fontSize="xl">{item.medal}</Text>
          </GridItem>
        </GridItem>
      ))}
    </>
  );
};

export default RankItem;
