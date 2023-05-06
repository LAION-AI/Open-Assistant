import { Box, Flex, Grid, Text } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { ReactNode } from "react";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { LeaderboardEntity, LeaderboardTimeFrame } from "src/types/Leaderboard";

import { SurveyCard } from "../Survey/SurveyCard";

export const UserStats = ({
  stats,
  title,
}: {
  stats: Partial<{ [time in LeaderboardTimeFrame]: LeaderboardEntity }>;
  title?: string;
}) => {
  const { t } = useTranslation("leaderboard");

  return (
    <SurveyCard>
      <Title>{title || t("your_stats")}</Title>
      {[LeaderboardTimeFrame.day, LeaderboardTimeFrame.week, LeaderboardTimeFrame.month, LeaderboardTimeFrame.total]
        .map((key) => ({ key, values: stats[key] }))
        .filter(({ values }) => values)
        .map(({ key, values }) => (
          <Box key={key} py={4}>
            <Title>{t(getTypeSafei18nKey(key))}</Title>
            <Flex w="full" wrap="wrap" alignItems="flex-start" gap={4}>
              <TableColumn>
                <Entry title={t("score")} value={values.leader_score} />
                <Entry title={t("rank")} value={values.rank} />
                <Entry title={t("prompt")} value={values.prompts} />
                <Entry title={t("accepted_prompts")} value={values.accepted_prompts} />
              </TableColumn>
              <TableColumn>
                <Entry title={t("replies_assistant")} value={values.replies_assistant} />
                <Entry title={t("accepted")} value={values.accepted_replies_assistant} />
                <Entry title={t("replies_prompter")} value={values.replies_prompter} />
                <Entry title={t("accepted")} value={values.accepted_replies_prompter} />
              </TableColumn>
              <TableColumn>
                <Entry title={t("labels_full")} value={values.labels_full} />
                <Entry title={t("labels_simple")} value={values.labels_simple} />
                <Entry title={t("rankings")} value={values.rankings_total} />
                <Entry title={t("reply_ranked_1")} value={values.reply_ranked_1} />
              </TableColumn>
            </Flex>
          </Box>
        ))}
    </SurveyCard>
  );
};

const Title = ({ children }: { children: ReactNode }) => (
  <Text as="b" display="block" fontSize="2xl" py={2}>
    {children}
  </Text>
);

const TableColumn = ({ children }: { children: ReactNode }) => {
  return (
    <Grid gridTemplateColumns="1fr max-content" mx={8} w="60" gap={2}>
      {children}
    </Grid>
  );
};

const Entry = ({ title, value }: { value: ReactNode; title: ReactNode }) => {
  return (
    <>
      <span className="text-start">{title}</span>
      <span className="text-end">{value}</span>
    </>
  );
};
