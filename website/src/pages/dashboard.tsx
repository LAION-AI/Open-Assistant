import Head from "next/head";
import { useSession } from "next-auth/react";
import { LeaderboardTable, TaskOption } from "src/components/Dashboard";
import { getDashboardLayout } from "src/components/Layout";
import { TaskCategory } from "src/components/Tasks/TaskTypes";
import {ComponentModal} from "src/components/Modal/Modal";

const Dashboard = () => {
  const { data: session } = useSession();

  // TODO(#670): Do something more meaningful when the user is new.
  console.log(session?.user?.isNew);

  return (
    <>
      <Head>
        <title>Dashboard - Open Assistant</title>
        <meta name="description" content="Chat with Open Assistant and provide feedback." />
      </Head>
      <TaskOption displayTaskCategories={[TaskCategory.Tasks]} />
      <LeaderboardTable />
      <ComponentModal onSkip={() => {
        console.log("Skip");
      }} />
    </>
  );
};

Dashboard.getLayout = (page) => getDashboardLayout(page);

export default Dashboard;
