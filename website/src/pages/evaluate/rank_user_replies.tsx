import { getDashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getServerSideProps } from "src/lib/defaultServerSideProps";

const RankPrompterReplies = () => <TaskPage type={TaskType.rank_prompter_replies} />;

RankPrompterReplies.getLayout = getDashboardLayout;

export default RankPrompterReplies;
