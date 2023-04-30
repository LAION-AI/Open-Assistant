import { Card, CardBody, Link, Text } from "@chakra-ui/react";
import NextLink from "next/link";
import { useTranslation } from "next-i18next";
import { LeaderboardTable } from "src/components/LeaderboardTable";
import { LeaderboardTimeFrame } from "src/types/Leaderboard";

export function LeaderboardWidget() {
  const { t } = useTranslation(["leaderboard"]);
  return (
    <main className="h-fit col-span-3">
      <div className="flex flex-col gap-4">
        <div className="flex items-end justify-between">
          <Text className="text-2xl font-bold">{t("top_5_contributors_today")}</Text>
          <Link as={NextLink} href="/leaderboard" _hover={{ textDecoration: "none" }}>
            <Text color="blue.400" className="text-sm font-bold">
              {t("view_all")} -&gt;
            </Text>
          </Link>
        </div>
        <Card>
          <CardBody>
            <LeaderboardTable timeFrame={LeaderboardTimeFrame.day} limit={5} rowPerPage={5} hideCurrentUserRanking />
          </CardBody>
        </Card>
      </div>
    </main>
  );
}
