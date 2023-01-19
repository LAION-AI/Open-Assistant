import Head from "next/head";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { TaskEmptyState } from "src/components/EmptyState";
import { getDashboardLayout } from "src/components/Layout";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import { useCreatePrompterReply } from "src/hooks/tasks/useCreateReply";

const UserReply = () => {
  const { tasks, isLoading, reset, trigger } = useCreatePrompterReply();

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length === 0) {
    return <TaskEmptyState />;
  }

  return (
    <>
      <Head>
        <title>Reply as User</title>
        <meta name="description" content="Reply as User." />
      </Head>
      <Task key={tasks[0].task.id} frontendId={tasks[0].id} task={tasks[0].task} trigger={trigger} mutate={reset} />
    </>
  );
};

UserReply.getLayout = getDashboardLayout;

export const getStaticProps = async ({ locale }) => ({
  props: {
    ...(await serverSideTranslations(locale, ["common"])),
  },
});

export default UserReply;
