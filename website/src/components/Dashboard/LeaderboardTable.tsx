import { Box, Link, Text, useColorModeValue } from "@chakra-ui/react";
import NextLink from "next/link";
import { LeaderboardGridCell } from "src/components/LeaderboardGridCell";
import { LeaderboardTimeFrame } from "src/types/Leaderboard";

export function LeaderboardTable() {
  const backgroundColor = useColorModeValue("white", "gray.700");
  const accentColor = useColorModeValue("gray.200", "gray.900");
  return (
    <main className="h-fit col-span-3">
      <div className="flex flex-col gap-4">
        <div className="flex items-end justify-between">
          <Text className="text-2xl font-bold">Top 5 Contributors Today</Text>
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
          <LeaderboardGridCell timeFrame={LeaderboardTimeFrame.day} />
        </Box>
      </div>
    </main>
  );
}
