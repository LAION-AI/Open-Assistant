import { useColorMode } from "@chakra-ui/react";
import Head from "next/head";
import { useEffect, useState } from "react";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import fetcher from "src/lib/fetcher";
import poster from "src/lib/poster";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

import CreateTask from "./CreateTask";
import EvaluateTask from "./EvaluateTask";
import { taskTypes } from "./TaskTypes";

const Task = ({ taskTypeName, taskName }) => {
  const taskType = taskTypes[taskTypeName][taskName];
  const [tasks, setTasks] = useState([]);

  const { isLoading, mutate } = useSWRImmutable(`/api/new_task/${taskType.endpoint}`, fetcher, {
    onSuccess: (data) => {
      setTasks([data]);
    },
  });

  useEffect(() => {
    if (tasks.length == 0) {
      mutate();
    }
  }, [tasks]);

  const { trigger } = useSWRMutation("/api/update_task", poster, {
    onSuccess: async (data) => {
      const newTask = await data.json();
      setTasks((oldTasks) => [...oldTasks, newTask]);
    },
  });

  const { colorMode } = useColorMode();
  const mainBgClasses = colorMode === "light" ? "bg-slate-300 text-gray-800" : "bg-slate-900 text-white";

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length == 0) {
    return (
      <div className={`p-12 ${mainBgClasses}`}>
        <div className="flex h-full">
          <div className="text-xl font-bold  mx-auto my-auto">No tasks found...</div>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>{taskType.label}</title>
        <meta name="description" content={taskType.label} />
      </Head>
      {taskTypeName == "create" ? (
        <CreateTask tasks={tasks} taskType={taskType} trigger={trigger} mutate={mutate} mainBgClasses={mainBgClasses} />
      ) : null}
      {taskTypeName == "evaluate" ? (
        <EvaluateTask
          tasks={tasks}
          taskType={taskType}
          trigger={trigger}
          mutate={mutate}
          mainBgClasses={mainBgClasses}
        />
      ) : null}
    </>
  );
};

export default Task;
