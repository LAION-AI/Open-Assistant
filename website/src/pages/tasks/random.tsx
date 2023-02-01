import { getDashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";
import { TaskType } from "src/types/Task";

const Random = () => <TaskPage type={TaskType.random} />;

Random.getLayout = getDashboardLayout;

export default Random;
