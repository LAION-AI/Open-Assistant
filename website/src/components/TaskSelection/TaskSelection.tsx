import { Flex } from "@chakra-ui/react";
import React from "react";

import { TaskOption } from "./TaskOption";
import { TaskOptions } from "./TaskOptions";

export const TaskSelection = () => {
  return (
    <Flex gap={10} wrap="wrap" justifyContent="space-evenly" width="full" height="full" alignItems={"center"}>
      <TaskOptions key="create" title="Create">
        {/* <TaskOption
          alt="Summarize Stories"
          img="/images/logos/logo.svg"
          title="Summarize stories"
          link="/create/summarize_story"
        /> */}
        <TaskOption alt="Reply as User" img="/images/logos/logo.svg" title="Reply as User" link="/create/user_reply" />
        <TaskOption
          alt="Reply as Assistant"
          img="/images/logos/logo.svg"
          title="Reply as Assistant"
          link="/create/assistant_reply"
        />
      </TaskOptions>
      <TaskOptions key="evaluate" title="Evaluate">
        {/*
        Commented out while the backend does not support them.
        <TaskOption
          alt="Rate Prompts"
          img="/images/logos/logo.svg"
          title="Rate Prompts"
          link="/evaluate/rate_summary"
        /> */}
        <TaskOption
          alt="Rank Initial Prompts"
          img="/images/logos/logo.svg"
          title="Rank Initial Prompts"
          link="/evaluate/rank_initial_prompts"
        />
        <TaskOption
          alt="Rank User Replies"
          img="/images/logos/logo.svg"
          title="Rank User Replies"
          link="/evaluate/rank_user_replies"
        />
        <TaskOption
          alt="Rank Assistant Replies"
          img="/images/logos/logo.svg"
          title="Rank Assistant Replies"
          link="/evaluate/rank_assistant_replies"
        />
      </TaskOptions>
    </Flex>
  );
};
