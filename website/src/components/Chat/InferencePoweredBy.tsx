import { Flex } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { Fragment } from "react";
import { TeamMember } from "src/components/TeamMember";

import data from "../../data/team.json";

const sponsors = ["hf", "stability", "redmond", "wandb"] as const;

const rootProps = {
  bg: "transparent",
  borderRadius: 0,
};

export const InferencePoweredBy = () => {
  const { t } = useTranslation("chat");
  return (
    <Flex direction="column" justifyContent="center" borderTopWidth="1px" p="2">
      <Flex justifyContent="center" pb="2" fontSize="sm" color="gray.500">
        {t("sponsored_by")}
      </Flex>
      {sponsors.map((id) => (
        <Fragment key={id}>
          <TeamMember {...data.people[id]} rootProps={rootProps}></TeamMember>
        </Fragment>
      ))}
    </Flex>
  );
};
