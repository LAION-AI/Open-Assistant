import React from "react";
import { Task } from "src/components/Tasks/Task";
import { TaskInfos } from "src/components/Tasks/TaskTypes";
import { TaskContext } from "src/context/TaskContext";

import { SessionDecorator } from "../../../../.storybook/decorators";

const story = {
  title: "tasks/Task",
  component: Task,
  decorators: [SessionDecorator],
};

const Template = ({ providerValue }) => {
  return (
    <TaskContext.Provider value={providerValue}>
      <Task />
    </TaskContext.Provider>
  );
};

const exampleProviderValue = {
  frontendId: "1234",
  task: {
    conversation: {
      messages: [
        {
          text: "I'm unsure how to interpret this. Is it a riddle?",
          is_assistant: true,
          id: "",
          frontend_message_id: "",
          emojis: {},
          user_emojis: [],
        },
        {
          text: "No, I just wanted to see how you reply when I type random characters. Can you tell me who invented Wikipedia?",
          is_assistant: false,
          id: "",
          frontend_message_id: "",
          emojis: { "-1": 11, red_flag: 2 },
          user_emojis: [],
        },
      ],
    },
    id: "1234-4321",
    mandatory_labels: ["spam"],
    message_id: "772f843e-f740-4aad-a44f-e3cf0260692c",
    reply: "1231231231",
    type: "label_prompter_reply",
    valid_labels: ["spam", "fails_task"],
    labels: [],
  },
  taskInfo: TaskInfos.find((t) => t.type === "label_prompter_reply"),
  isLoading: false,
  completeTask: (content) => {
    console.log(content);
  },
  skipTask: () => {
    console.log("skip");
  },
  rejectTask: () => {
    console.log("reject");
  },
};

export const Default = Template.bind({});
Default.args = { providerValue: exampleProviderValue };

export default story;
