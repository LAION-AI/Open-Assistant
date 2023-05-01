import { DashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
export { getStaticProps } from "src/lib/defaultServerSideProps";
import { TaskType } from "src/types/Task";

const Random = () => <TaskPage type={TaskType.random} />;

Random.getLayout = DashboardLayout;

export default Random;
