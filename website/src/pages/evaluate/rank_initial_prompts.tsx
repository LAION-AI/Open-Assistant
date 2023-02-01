import { getDashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";

const RankInitialPrompts = () => <TaskPage type={TaskType.rank_initial_prompts} />;

RankInitialPrompts.getLayout = getDashboardLayout;

export default RankInitialPrompts;
