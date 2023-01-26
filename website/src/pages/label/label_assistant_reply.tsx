import { getDashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";

const LabelAssistantReply = () => <TaskPage type={TaskType.label_assistant_reply} />;

LabelAssistantReply.getLayout = getDashboardLayout;

export default LabelAssistantReply;
