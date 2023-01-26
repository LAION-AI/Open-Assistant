import { getDashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";

const RankAssistantReplies = () => <TaskPage type={TaskType.rank_assistant_replies} />;

RankAssistantReplies.getLayout = getDashboardLayout;

export default RankAssistantReplies;
