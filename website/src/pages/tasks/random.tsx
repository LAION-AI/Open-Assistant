import Head from "next/head";
import { FiAlertTriangle } from "react-icons/fi";
import { EmptyState } from "src/components/EmptyState";
import { getDashboardLayout } from "src/components/Layout";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import { useGenericTaskAPI } from "src/hooks/tasks/useGenericTaskAPI";

const RandomTask = () => {
  const { tasks, isLoading, trigger, reset } = useGenericTaskAPI("random");

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length === 0) {
    return <EmptyState text="Looks like no tasks were found." icon={FiAlertTriangle} />;
  }

  return (
    <>
      <Head>
        <title>Random Task</title>
        <meta name="description" content="Random Task." />
      </Head>
      <Task key={tasks[0].task.id} frontendId={tasks[0].id} task={tasks[0].task} trigger={trigger} mutate={reset} />
    </>
  );
};

RandomTask.getLayout = (page) => getDashboardLayout(page);

export default RandomTask;
