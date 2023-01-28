import React from "react";

import { Task } from "./Task";

export default {
  title: "tasks/Task",
  component: Task,
};

const Template = ({ frontendId, task, isLoading, completeTask, skipTask }) => {
  return (
    <Task frontendId={frontendId} task={task} isLoading={isLoading} completeTask={completeTask} skipTask={skipTask} />
  );
};

export const Default = Template.bind({});
Default.args = {
  frontendId: "1234",
  task: {
    conversation: [],
    id: "1234-4321",
    mandatory_labels: ["spam"],
    message_id: "772f843e-f740-4aad-a44f-e3cf0260692c",
    reply: "1231231231",
    type: "label_prompter_reply",
    valid_labels: ["spam", "fails_task"],
  },
  isLoading: false,
  completeTask: (id, update_type, content) => {
    console.log(content);
  },
  skipTask: () => {
    console.log("skip");
  },
};
