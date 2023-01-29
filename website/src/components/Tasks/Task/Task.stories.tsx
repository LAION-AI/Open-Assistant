import React from "react";
import { Task } from "src/components/Tasks/Task";
import { TaskInfos } from "src/components/Tasks/TaskTypes";
import { TaskContext } from "src/context/TaskContext";

export default {
  title: "tasks/Task",
  component: Task,
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
    conversation: [],
    id: "1234-4321",
    mandatory_labels: ["spam"],
    message_id: "772f843e-f740-4aad-a44f-e3cf0260692c",
    reply: "1231231231",
    type: "label_prompter_reply",
    valid_labels: ["spam", "fails_task"],
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
