import { Box, Link, Stack, StackDivider, Text, useColorModeValue } from "@chakra-ui/react";
import NextLink from "next/link";
import { get } from "src/lib/api";
import useSWR from "swr";

export function LeaderboardTable() {
  const backgroundColor = useColorModeValue("white", "gray.700");
  const accentColor = useColorModeValue("gray.200", "gray.900");
  const { data: leaderboardEntries } = useSWR("/api/leaderboard", get);
  return (
    <main className="h-fit col-span-3">
      <div className="flex flex-col gap-4">
        <div className="flex items-end justify-between">
          <Text className="text-2xl font-bold">Top 5 Contributors</Text>
          <Link as={NextLink} href="/leaderboard" _hover={{ textDecoration: "none" }}>
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
            {leaderboardEntries?.map(({ display_name, score }, idx) => (
              <div key={idx} className="grid grid-cols-4 items-center">
                <div className="flex items-center gap-3">
                  {/*
                  <Image alt="Profile Picture" src={item.image} boxSize="7" borderRadius="full"></Image>
                    */}
                  <p>{display_name}</p>
                  {/*
                  <Badge colorScheme="purple">{item.streakCount}</Badge>
                    */}
                </div>
                <Box bg={backgroundColor} className="col-start-4 flex justify-center">
                  <p>{score}</p>
                </Box>
              </div>
            ))}
          </Stack>
        </Box>
      </div>
    </main>
  );
}
