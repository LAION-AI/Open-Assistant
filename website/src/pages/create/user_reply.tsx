import { useColorMode } from "@chakra-ui/react";
import Head from "next/head";
import { useEffect, useState } from "react";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import fetcher from "src/lib/fetcher";
import poster from "src/lib/poster";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

const UserReply = () => {
  const [tasks, setTasks] = useState([]);

  const { isLoading, mutate } = useSWRImmutable("/api/new_task/prompter_reply", fetcher, {
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
        <title>Reply as Assistant</title>
        <meta name="description" content="Reply as Assistant." />
      </Head>
      <Task tasks={tasks} trigger={trigger} mutate={mutate} mainBgClasses={mainBgClasses} />
    </>
  );
};

export default UserReply;
