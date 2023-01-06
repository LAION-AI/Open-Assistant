import { useState } from "react";
import { ContextMessages } from "src/components/ContextMessages";
import { Message } from "src/components/Messages";
import { Sortable } from "src/components/Sortable/Sortable";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { TaskControlsOverridable } from "src/components/Survey/TaskControlsOverridable";

const EvaluateTask = ({ tasks, taskType, trigger, mutate, mainBgClasses }) => {
  /**
   * This array will contain the ranked indices of the replies
   * The best reply will have index 0, and the worst is the last.
   */
  const [ranking, setRanking] = useState<number[]>([]);

  const submitResponse = (task) => {
    trigger({
      id: task.id,
      update_type: "message_ranking",
      content: {
        ranking,
      },
    });
  };

  const fetchNextTask = () => {
    setRanking([]);
    mutate();
  };

  const sortableItems = tasks[0].task[taskType.sortable] as string[];
  let messages = null;
  if (tasks[0].task.conversation && tasks[0].task.conversation.messages) {
    messages = tasks[0].task.conversation.messages as Message[];
  }

  return (
    <div className={`p-12 ${mainBgClasses}`}>
      <SurveyCard className="max-w-7xl mx-auto h-fit mb-24">
        <h5 className="text-lg font-semibold mb-4">{taskType.header}</h5>
        <p className="text-lg py-1">{taskType.instructions}</p>
        <ContextMessages messages={messages} />
        <Sortable items={sortableItems} onChange={setRanking} className="my-8" />
      </SurveyCard>

      <TaskControlsOverridable
        tasks={tasks}
        isValid={ranking.length == tasks[0].task[taskType.sortable].length}
        prepareForSubmit={() => setRanking(tasks[0].task[taskType.sortable].map((_, idx) => idx))}
        onSubmitResponse={submitResponse}
        onSkip={fetchNextTask}
      />
    </div>
  );
};

export default EvaluateTask;
