import { getDashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";

const InitialPrompt = () => <TaskPage type={TaskType.initial_prompt} />;

InitialPrompt.getLayout = getDashboardLayout;

export default InitialPrompt;
