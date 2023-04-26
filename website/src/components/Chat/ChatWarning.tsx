import { Flex } from "@chakra-ui/react";
import { Fragment } from "react";
import { TeamMember } from "src/components/TeamMember";

import data from "../../data/warning.json";

const warn = ["warning"] as const;

const rootProps = {
  bg: "transparent",
  borderRadius: 0,
};

export const ChatWarning = () => {
  return (
    <Flex direction="column" justifyContent="center" borderTopWidth="1px" p="2">
      {warn.map((id) => (
        <Fragment key={id}>
          <TeamMember {...data.panels[id]} rootProps={rootProps}></TeamMember>
        </Fragment>
      ))}
      <Flex justifyContent="center" pb="2" fontSize="sm" color="gray.500">
        Usage Warning
      </Flex>
    </Flex>
  );
};
