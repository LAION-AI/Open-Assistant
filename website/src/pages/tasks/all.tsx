import Head from "next/head";
import { TaskOption } from "src/components/Dashboard";
import { getDashboardLayout } from "src/components/Layout";
import { TaskCategory } from "src/components/Tasks/TaskTypes";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";

const AllTasks = () => {
  return (
    <>
      <Head>
        <title>All Tasks - Open Assistant</title>
        <meta name="description" content="All tasks for Open Assistant." />
      </Head>
      <TaskOption displayTaskCategories={[TaskCategory.Create, TaskCategory.Evaluate, TaskCategory.Label]} />
    </>
  );
};

AllTasks.getLayout = (page) => getDashboardLayout(page);

export default AllTasks;
