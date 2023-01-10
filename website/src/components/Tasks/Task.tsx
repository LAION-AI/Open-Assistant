import { useColorMode } from "@chakra-ui/react";
import { CreateTask } from "src/components/Tasks/CreateTask";
import { EvaluateTask } from "src/components/Tasks/EvaluateTask";
import { LabelTask } from "src/components/Tasks/LabelTask";
import { TaskCategory, TaskTypes } from "src/components/Tasks/TaskTypes";
import poster from "src/lib/poster";
import useSWRMutation from "swr/mutation";

export const Task = ({ tasks, trigger, mutate }) => {
  const task = tasks[0].task;

  const { colorMode } = useColorMode();
  const mainBgClasses = colorMode === "light" ? "bg-slate-300 text-gray-800" : "bg-slate-900 text-white";

  const { trigger: sendRejection } = useSWRMutation("/api/reject_task", poster, {
    onSuccess: async () => {
      mutate();
    },
  });

  const rejectTask = (task: { id: string }, reason: string) => {
    sendRejection({
      id: task.id,
      reason,
    });
  };

  function taskTypeComponent(type) {
    const taskType = TaskTypes.find((taskType) => taskType.type === type);
    const category = taskType.category;
    switch (category) {
      case TaskCategory.Create:
        return (
          <CreateTask
            tasks={tasks}
            trigger={trigger}
            onSkipTask={rejectTask}
            onNextTask={mutate}
            taskType={taskType}
            mainBgClasses={mainBgClasses}
          />
        );
      case TaskCategory.Evaluate:
        return (
          <EvaluateTask
            tasks={tasks}
            trigger={trigger}
            onSkipTask={rejectTask}
            onNextTask={mutate}
            mainBgClasses={mainBgClasses}
          />
        );
      case TaskCategory.Label:
        return (
          <LabelTask
            tasks={tasks}
            taskType={taskType}
            trigger={trigger}
            onSkipTask={rejectTask}
            onNextTask={mutate}
            mainBgClasses={mainBgClasses}
          />
        );
    }
  }

  return taskTypeComponent(task.type);
};
