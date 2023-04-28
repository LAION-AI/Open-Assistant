import { DashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getStaticProps } from "src/lib/defaultServerSideProps";

const LabelAssistantReply = () => <TaskPage type={TaskType.label_assistant_reply} />;

LabelAssistantReply.getLayout = DashboardLayout;

export default LabelAssistantReply;
