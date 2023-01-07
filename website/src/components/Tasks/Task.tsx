import { CreateTask } from "./CreateTask";
import { EvaluateTask } from "./EvaluateTask";
import { TaskCategory, TaskTypes } from "./TaskTypes";

export const Task = ({ tasks, trigger, mutate, mainBgClasses }) => {
  const task = tasks[0].task;

  function taskTypeComponent(type) {
    const taskType = TaskTypes.find((taskType) => taskType.type === type);
    const category = taskType.category;
    switch (category) {
      case TaskCategory.Create:
        return (
          <CreateTask
            tasks={tasks}
            trigger={trigger}
            mutate={mutate}
            taskType={taskType}
            mainBgClasses={mainBgClasses}
          />
        );
      case TaskCategory.Evaluate:
        return <EvaluateTask tasks={tasks} trigger={trigger} mutate={mutate} mainBgClasses={mainBgClasses} />;
    }
  }

  return taskTypeComponent(task.type);
};
