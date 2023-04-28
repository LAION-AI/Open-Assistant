import { DashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getStaticProps } from "src/lib/defaultServerSideProps";

const RankInitialPrompts = () => <TaskPage type={TaskType.rank_initial_prompts} />;

RankInitialPrompts.getLayout = DashboardLayout;

export default RankInitialPrompts;
