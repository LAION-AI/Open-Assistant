import { DashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getStaticProps } from "src/lib/defaultServerSideProps";

const LabelPrompterReply = () => <TaskPage type={TaskType.label_prompter_reply} />;

LabelPrompterReply.getLayout = DashboardLayout;

export default LabelPrompterReply;
