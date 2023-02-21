import { Box, useBoolean, useColorModeValue } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { useEffect, useState } from "react";
import { LabelInputGroup } from "src/components/Messages/LabelInputGroup";
import { MessageConversation } from "src/components/Messages/MessageConversation";
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";
import { TaskSurveyProps } from "src/components/Tasks/Task";
import { TaskHeader } from "src/components/Tasks/TaskHeader";
import { LabelTaskReply } from "src/types/TaskResponses";
import { LabelTaskType } from "src/types/Tasks";

const isRequired = (labelName: string, requiredLabels?: string[]) => {
  return requiredLabels ? requiredLabels.includes(labelName) : false;
};

export const LabelTask = ({
  task,
  taskType,
  isEditable,
  onReplyChanged,
  onValidityChanged,
}: TaskSurveyProps<LabelTaskType, LabelTaskReply>) => {
  const { t } = useTranslation("labelling");
  const [values, setValues] = useState<number[]>(new Array(task.labels.length).fill(null));
  const [userInputMade, setUserInputMade] = useBoolean(false);

  // Initial setup to run when the task changes
  useEffect(() => {
    setValues(new Array(task.labels.length).fill(null));
    onValidityChanged(task.labels.some(({ name }) => isRequired(name, task.mandatory_labels)) ? "INVALID" : "DEFAULT");
    setUserInputMade.off();
  }, [task, setUserInputMade, onValidityChanged]);

  // Update the reply and validity when the values change
  useEffect(() => {
    onReplyChanged({
      text: "unused?",
      labels: Object.fromEntries(task.labels.map(({ name }, idx) => [name, values[idx] || 0])),
      message_id: task.message_id,
    });
    onValidityChanged(
      task.labels.some(({ name }, idx) => values[idx] === null && isRequired(name, task.mandatory_labels))
        ? "INVALID"
        : userInputMade
        ? "VALID"
        : "DEFAULT"
    );
  }, [task, values, onReplyChanged, userInputMade, onValidityChanged]);

  const cardColor = useColorModeValue("gray.50", "gray.800");
  const isSpamTask = task.mode === "simple" && task.valid_labels.length === 1 && task.valid_labels[0] === "spam";

  const lastMessage = task.conversation.messages[task.conversation.messages.length - 1];
  return (
    <div data-cy="task" data-task-type={isSpamTask ? "spam-task" : "label-task"}>
      <TwoColumnsWithCards>
        <>
          <TaskHeader taskType={taskType} />
          <Box mt="4" p={[4, 6]} borderRadius="lg" bg={cardColor}>
            <MessageConversation messages={task.conversation.messages} highlightLastMessage />
          </Box>
        </>
        <LabelInputGroup
          labels={task.labels}
          values={values}
          requiredLabels={task.mandatory_labels}
          isEditable={isEditable}
          instructions={{
            yesNoInstruction: t("label_highlighted_yes_no_instruction"),
            flagInstruction: t("label_highlighted_flag_instruction"),
            likertInstruction: t("label_highlighted_likert_instruction"),
          }}
          expectedLanguage={lastMessage.lang}
          onChange={(values) => {
            setValues(values);
            setUserInputMade.on();
          }}
        />
      </TwoColumnsWithCards>
    </div>
  );
};
