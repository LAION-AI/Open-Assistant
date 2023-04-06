import { DashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getStaticProps } from "src/lib/defaultServerSideProps";

const LabelInitialPrompt = () => <TaskPage type={TaskType.label_initial_prompt} />;

LabelInitialPrompt.getLayout = DashboardLayout;

export default LabelInitialPrompt;
