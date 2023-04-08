import { getDashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getServerSideProps } from "src/lib/defaultServerSideProps";

const LabelAssistantReply = () => <TaskPage type={TaskType.label_assistant_reply} />;

LabelAssistantReply.getLayout = getDashboardLayout;

export default LabelAssistantReply;
