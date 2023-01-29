import { getDashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";

const PrompterReply = () => <TaskPage type={TaskType.prompter_reply} />;

PrompterReply.getLayout = getDashboardLayout;

export default PrompterReply;
