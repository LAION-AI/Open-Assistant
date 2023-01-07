import { CreateTask } from "./CreateTask";
import { EvaluateTask } from "./EvaluateTask";
import { TaskTypes } from "./TaskTypes";

export const Task = ({ tasks, trigger, mutate, mainBgClasses }) => {
  const task = tasks[0].task;

  function taskTypeComponent(type) {
    const category = TaskTypes.find((taskType) => taskType.type === type).category;

    switch (category) {
      case "create":
        return <CreateTask tasks={tasks} trigger={trigger} mutate={mutate} mainBgClasses={mainBgClasses} />;
      case "evaluate":
        return <EvaluateTask tasks={tasks} trigger={trigger} mutate={mutate} mainBgClasses={mainBgClasses} />;
    }
  }

  return taskTypeComponent(task.type);
};
