import { DashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getStaticProps } from "src/lib/defaultServerSideProps";

const AssistantReply = () => <TaskPage type={TaskType.assistant_reply} />;

AssistantReply.getLayout = DashboardLayout;

export default AssistantReply;
