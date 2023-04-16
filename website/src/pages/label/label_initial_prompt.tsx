import { getDashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getServerSideProps } from "src/lib/defaultServerSideProps";

const LabelInitialPrompt = () => <TaskPage type={TaskType.label_initial_prompt} />;

LabelInitialPrompt.getLayout = getDashboardLayout;

export default LabelInitialPrompt;
