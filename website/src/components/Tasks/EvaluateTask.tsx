import { useEffect } from "react";
import { MessageTable } from "src/components/Messages/MessageTable";
import { Sortable } from "src/components/Sortable/Sortable";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { TaskSurveyProps } from "src/components/Tasks/Task";

export const EvaluateTask = ({ task, onReplyChanged }: TaskSurveyProps<{ ranking: number[] }>) => {
  let messages = [];
  if (task.conversation) {
    messages = task.conversation.messages;
    messages = messages.map((message, index) => ({ ...message, id: index }));
  }

  useEffect(() => {
    const conversationMsgs = task.conversation ? task.conversation.messages : [];
    const defaultRanking = conversationMsgs.map((message, index) => index);
    onReplyChanged({
      content: { ranking: defaultRanking },
      state: "DEFAULT",
    });
  }, [task.conversation, onReplyChanged]);

  const onRank = (newRanking: number[]) => {
    onReplyChanged({ content: { ranking: newRanking }, state: "VALID" });
  };

  const sortables = task.replies ? "replies" : "prompts";

  return (
    <SurveyCard className="max-w-7xl mx-auto h-fit mb-24">
      <h5 className="text-lg font-semibold mb-4">Instructions</h5>
      <p className="text-lg py-1">
        Given the following {sortables}, sort them from best to worst, best being first, worst being last.
      </p>
      <MessageTable messages={messages} />
      <Sortable items={task[sortables]} onChange={onRank} className="my-8" />
    </SurveyCard>
  );
};
