import { DashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getStaticProps } from "src/lib/defaultServerSideProps";

const InitialPrompt = () => <TaskPage type={TaskType.initial_prompt} />;

InitialPrompt.getLayout = DashboardLayout;

export default InitialPrompt;
