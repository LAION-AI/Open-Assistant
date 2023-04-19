import { Flex } from "@chakra-ui/react";
import { Fragment } from "react";
import { TeamMember } from "src/components/TeamMember";

import data from "../../data/team.json";

const sponsors = ["hf", "stability", "redmond", "wandb"] as const;

export const InferencePoweredBy = () => {
  return (
    <Flex
      direction="column"
      bg="blackAlpha.50"
      _dark={{
        bg: "whiteAlpha.50",
      }}
      justifyContent="center"
    >
      {sponsors.map((id) => (
        <Fragment key={id}>
          <TeamMember
            {...data.people[id]}
            rootProps={{
              bg: "transparent",
              borderRadius: 0,
            }}
          ></TeamMember>
        </Fragment>
      ))}
      <Flex justifyContent="center" pb="2" fontSize="sm" color="gray.500">
        Sponsored By
      </Flex>
    </Flex>
  );
};
