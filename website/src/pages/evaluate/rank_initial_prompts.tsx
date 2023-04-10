import { getDashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getServerSideProps } from "src/lib/defaultServerSideProps";

const RankInitialPrompts = () => <TaskPage type={TaskType.rank_initial_prompts} />;

RankInitialPrompts.getLayout = getDashboardLayout;

export default RankInitialPrompts;
