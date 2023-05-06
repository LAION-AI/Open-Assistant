import { DashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getStaticProps } from "src/lib/defaultServerSideProps";

const RankAssistantReplies = () => <TaskPage type={TaskType.rank_assistant_replies} />;

RankAssistantReplies.getLayout = DashboardLayout;

export default RankAssistantReplies;
