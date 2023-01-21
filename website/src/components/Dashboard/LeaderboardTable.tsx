import { Card, CardBody, Flex, Link, Text } from "@chakra-ui/react";
import NextLink from "next/link";
import { LeaderboardGridCell } from "src/components/LeaderboardGridCell";
import { LeaderboardTimeFrame } from "src/types/Leaderboard";

export function LeaderboardTable() {
  return (
    <main className="h-fit col-span-3">
      <Flex direction="column" gap="4">
        <Flex alignItems="end" justifyContent="space-between">
          <Text variant="h1">Top 5 Contributors Today</Text>
          <Link as={NextLink} href="/leaderboard" _hover={{ textDecoration: "none" }}>
            <Text color="blue.400" className="text-sm font-bold">
              View All -&gt;
            </Text>
          </Link>
        </Flex>
        <Card>
          <CardBody>
            <LeaderboardGridCell timeFrame={LeaderboardTimeFrame.day} />
          </CardBody>
        </Card>
      </Flex>
    </main>
  );
}
