import { getDashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getServerSideProps } from "src/lib/defaultServerSideProps";

const LabelPrompterReply = () => <TaskPage type={TaskType.label_prompter_reply} />;

LabelPrompterReply.getLayout = getDashboardLayout;

export default LabelPrompterReply;
