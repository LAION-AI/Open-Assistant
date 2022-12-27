import React from "react";
import { TaskOptions } from "./TaskOptions";
import { Flex } from "@chakra-ui/react";
import { TaskOption } from "./TaskOption";

export const TaskSelection = () => {
  return (
    <Flex gap={10} wrap="wrap" justifyContent="space-evenly" width="full" height="full" alignItems={"center"}>
      <TaskOptions key="create" title="Create">
        <TaskOption
          alt="Summarize Stories"
          img="/images/logos/logo.svg"
          title="Summarize stories"
          link="/summarize/story"
        />
      </TaskOptions>
      <TaskOptions key="evaluate" title="Evaluate">
        <TaskOption alt="Rate Summaries" img="/images/logos/logo.svg" title="Rate Summaries" link="/summarize/story" />
      </TaskOptions>
    </Flex>
  );
};
