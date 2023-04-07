import { Card, CardBody, CardHeader, Grid, Heading } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import React from "react";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { Stats as StatsType } from "src/types/Stat";

import { MessageTreeStateStatsStacked, MessageTreeStateStatsTable, statComponents } from "./Stats.components";

type StatsProps = {
  data: StatsType | undefined;
};

const CHART_STATS = [
  "human_messages_by_role",
  "message_trees_by_state",
  "human_messages_by_lang",
  "message_trees_states_by_lang",
];

export const Stats = ({ data }: StatsProps) => {
  const { t } = useTranslation("stats");

  if (!data) {
    return null;
  }

  const charts = Object.keys(data.stats_by_name).filter((key) => CHART_STATS.includes(key));

  const getStatByName = (name: string) => data.stats_by_name[name];

  const messageTreeStats = getStatByName("message_trees_states_by_lang");

  // this will be empty on a fresh db:
  if (!messageTreeStats) {
    return null;
  }

  return (
    <Grid gridTemplateColumns="repeat(2, minmax(0, 1fr))" gap={4}>
      <Heading size="lg" gridColumn="span 2">
        {t("stats")}
      </Heading>
      {charts.map((key) => {
        const stat = getStatByName(key);
        const component = statComponents[key];
        return (
          <Card key={key} minH={500} gridColumn={["span 2", "span 2", "span 1"]}>
            <CardHeader>
              <Heading size="md">{t(getTypeSafei18nKey(stat.name))}</Heading>
            </CardHeader>
            <CardBody>{component?.({ stat })}</CardBody>
          </Card>
        );
      })}
      <Card minH={500} gridColumn="span 2">
        <CardHeader>
          <Heading size="md">{t(getTypeSafei18nKey(messageTreeStats.name))}</Heading>
        </CardHeader>
        <CardBody>
          <MessageTreeStateStatsTable stat={messageTreeStats} />
        </CardBody>
      </Card>
      <Card minH={500} gridColumn="span 2">
        <CardHeader>
          <Heading size="md">{t(getTypeSafei18nKey(messageTreeStats.name))}</Heading>
        </CardHeader>
        <CardBody>
          <MessageTreeStateStatsStacked stat={messageTreeStats} />
        </CardBody>
      </Card>
    </Grid>
  );
};
