import { Badge, Box, Image, Link, Stack, StackDivider, Text, useColorModeValue } from "@chakra-ui/react";

export function LeaderboardTable() {
  const backgroundColor = useColorModeValue("white", "gray.700");
  const accentColor = useColorModeValue("gray.200", "gray.900");

  //need to add streak info to chart

  const leaderInfo = [
    {
      name: "fozziethebeat#6690",
      image: "/images/temp-avatars/av1.jpg",
      score: "5,208",
      arrowDir: "increase",
      streak: false,
      streakCount: "5-Day Streak",
    },
    {
      name: "k_nearest_neighbor#8579",
      image: "/images/temp-avatars/av2.jpg",
      score: "5,164",
      arrowDir: "decrease",
      streak: false,
      streakCount: "",
    },
    {
      name: "andreaskoepf#2266",
      image: "/images/temp-avatars/av3.jpg",
      score: "5,120",
      arrowDir: "",
      streak: false,
      streakCount: "2-Day Streak",
    },
    {
      name: "AbdBarho#1684",
      image: "/images/temp-avatars/av4.jpg",
      score: "4,260",
      arrowDir: "",
      streak: false,
      streakCount: "",
    },
    {
      name: "zu#9016",
      image: "/images/temp-avatars/av5.jpg",
      score: "3,608",
      arrowDir: "",
      streak: false,
      streakCount: "",
    },
  ];

  return (
    <main className="h-fit col-span-3">
      <div className="flex flex-col gap-4">
        <div className="flex items-end justify-between">
          <Text className="text-2xl font-bold">Top 5 Contributors</Text>
          <Link href="#" _hover={{ textDecoration: "none" }}>
            <Text color="blue.400" className="text-sm font-bold">
              View All -&gt;
            </Text>
          </Link>
        </div>
        <Box
          backgroundColor={backgroundColor}
          boxShadow="base"
          dropShadow={accentColor}
          borderRadius="xl"
          className="p-6 shadow-sm"
        >
          <Stack divider={<StackDivider />} spacing="4">
            <div className="grid grid-cols-4 items-center font-bold">
              <p>Name</p>
              <div className="col-start-4 flex justify-center">
                <p>Score</p>
              </div>
            </div>
            {leaderInfo.map((item, itemIndex) => (
              <div key={itemIndex} className="grid grid-cols-4 items-center">
                <div className="flex items-center gap-3">
                  <Image alt="Profile Picture" src={item.image} boxSize="7" borderRadius="full"></Image>
                  <p>{item.name}</p>
                  <Badge colorScheme="purple">{item.streakCount}</Badge>
                </div>
                <Box bg={backgroundColor} className="col-start-4 flex justify-center">
                  <p>{item.score}</p>
                </Box>
              </div>
            ))}
          </Stack>
        </Box>
      </div>
    </main>
  );
}
