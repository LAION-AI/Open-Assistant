import { getDashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";

const LabelPrompterReply = () => <TaskPage type={TaskType.label_prompter_reply} />;

LabelPrompterReply.getLayout = getDashboardLayout;

export default LabelPrompterReply;
