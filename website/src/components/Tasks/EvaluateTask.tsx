import { useState } from "react";
import { Sortable } from "src/components/Sortable/Sortable";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { TaskControlsOverridable } from "src/components/Survey/TaskControlsOverridable";

import { MessageTable } from "../Messages/MessageTable";

export interface EvaluateTaskProps {
  // we need a task type
  // eslint-disable-next-line  @typescript-eslint/no-explicit-any
  tasks: any[];
  trigger: (update: { id: string; update_type: string; content: { ranking: number[] } }) => void;
  onSkipTask: (task: { id: string }, reason: string) => void;
  onNextTask: () => void;
  mainBgClasses: string;
}

export const EvaluateTask = ({ tasks, trigger, onSkipTask, onNextTask, mainBgClasses }: EvaluateTaskProps) => {
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

  let messages = null;
  if (tasks[0].task.conversation) {
    messages = tasks[0].task.conversation.messages;
    messages = messages.map((message, index) => ({ ...message, id: index }));
  }

  const sortables = tasks[0].task.replies ? "replies" : "prompts";

  return (
    <div className={`p-12 ${mainBgClasses}`}>
      <SurveyCard className="max-w-7xl mx-auto h-fit mb-24">
        <h5 className="text-lg font-semibold mb-4">Instructions</h5>
        <p className="text-lg py-1">
          Given the following {sortables}, sort them from best to worst, best being first, worst being last.
        </p>
        {messages ? <MessageTable messages={messages} /> : null}
        <Sortable items={tasks[0].task[sortables]} onChange={setRanking} className="my-8" />
      </SurveyCard>

      <TaskControlsOverridable
        tasks={tasks}
        isValid={ranking.length == tasks[0].task[sortables].length}
        prepareForSubmit={() => setRanking(tasks[0].task[sortables].map((_, idx) => idx))}
        onSubmitResponse={submitResponse}
        onSkipTask={(task, reason) => {
          setRanking([]);
          onSkipTask(task, reason);
        }}
        onNextTask={onNextTask}
      />
    </div>
  );
};
