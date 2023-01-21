import React from "react";

import { Task } from "./Task";

export default {
  title: "tasks/Task",
  component: Task,
};

const Template = ({ frontendId, task, trigger, mutate }) => {
  return <Task frontendId={frontendId} task={task} trigger={trigger} mutate={mutate} />;
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
  trigger: (id, update_type, content) => {
    console.log(content);
  },
  mutate: () => {
    console.log("mutate");
  },
};
