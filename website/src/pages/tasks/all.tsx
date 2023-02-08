import Head from "next/head";
import { TaskOption } from "src/components/Dashboard";
import { allTaskOptions } from "src/components/Dashboard/TaskOption";
import { getDashboardLayout } from "src/components/Layout";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";

const AllTasks = () => {
  return (
    <>
      <Head>
        <title>All Tasks - Open Assistant</title>
        <meta name="description" content="All tasks for Open Assistant." />
      </Head>
      <TaskOption content={allTaskOptions} />
    </>
  );
};

AllTasks.getLayout = getDashboardLayout;

export default AllTasks;
