import { Card, CardBody, CardHeader, Divider, GridItem, Heading, SimpleGrid } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import React from "react";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { Stat, Stats as StatsType } from "src/types/Stat";

import { statComponents } from "./Stats.components";

type StatsProps = {
  data: StatsType | undefined;
};

export const Stats = ({ data }: StatsProps) => {
  const { t } = useTranslation("stats");

  if (!data) {
    return null;
  }

  const keys = Object.keys(data.stats_by_name).filter((key) => key !== "users_accepted_tos");

  // Add a second copy of the message_trees_states_by_lang
  // for creating the table in addition to the chart
  keys.push("message_trees_states_by_lang_table");
  data.stats_by_name["message_trees_states_by_lang_table"] = data.stats_by_name["message_trees_states_by_lang"];

  const getStatByName = (name: string): Stat => {
    return data.stats_by_name[name];
  };

  return (
    <>
      <Heading size="lg" className="pb-4">
        {t("stats")}
      </Heading>
      <SimpleGrid spacing={2} columns={{ base: 1, md: 2, lg: 2 }}>
        {keys.map((key) => {
          const stat = getStatByName(key);
          const component = statComponents[key];
          const colSpan = key === "message_trees_states_by_lang_table" ? 2 : 1;
          return (
            <GridItem key={key} colSpan={colSpan}>
              <Card minH={500}>
                <CardHeader>
                  <Heading size="md">{t(getTypeSafei18nKey(stat.name))}</Heading>
                </CardHeader>
                <Divider />
                <CardBody>{component?.({ stat })}</CardBody>
              </Card>
            </GridItem>
          );
        })}
      </SimpleGrid>
    </>
  );
};
