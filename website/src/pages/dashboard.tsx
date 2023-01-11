import Head from "next/head";
import { LeaderboardTable, TaskOption } from "src/components/Dashboard";
import { getDashboardLayout } from "src/components/Layout";
import { TaskCategory } from "src/components/Tasks/TaskTypes";

const Dashboard = () => {
  return (
    <>
      <Head>
        <title>Dashboard - Open Assistant</title>
        <meta name="description" content="Chat with Open Assistant and provide feedback." />
      </Head>
      <TaskOption displayTaskCategories={[TaskCategory.Tasks]} />
      <LeaderboardTable />
    </>
  );
};

Dashboard.getLayout = (page) => getDashboardLayout(page);

export default Dashboard;
