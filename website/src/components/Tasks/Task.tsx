import { CreateTask } from "src/components/Tasks/CreateTask";
import { EvaluateTask } from "src/components/Tasks/EvaluateTask";
import { TaskCategory, TaskTypes } from "src/components/Tasks/TaskTypes";
import poster from "src/lib/poster";
import useSWRMutation from "swr/mutation";

export const Task = ({ tasks, trigger, mutate, mainBgClasses }) => {
  const task = tasks[0].task;

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
    }
  }

  return taskTypeComponent(task.type);
};
