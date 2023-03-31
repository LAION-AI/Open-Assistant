import { getDashboardLayout } from "src/components/Layout";
import { TaskPage } from "src/components/TaskPage/TaskPage";
import { TaskType } from "src/types/Task";
export { getStaticProps } from "src/lib/defaultServerSideProps";

const PrompterReply = () => <TaskPage type={TaskType.prompter_reply} />;

PrompterReply.getLayout = getDashboardLayout;

export default PrompterReply;
