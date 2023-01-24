import Head from "next/head";
import { TaskEmptyState } from "src/components/EmptyState";
import { getDashboardLayout } from "src/components/Layout";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import { useGenericTaskAPI } from "src/hooks/tasks/useGenericTaskAPI";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";
import { TaskType } from "src/types/Task";

const RandomTask = () => {
  const { tasks, isLoading, trigger, reset } = useGenericTaskAPI(TaskType.random);

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length === 0) {
    return <TaskEmptyState />;
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
