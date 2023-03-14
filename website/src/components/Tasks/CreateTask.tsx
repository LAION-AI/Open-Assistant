import { Box, Stack, Tab, TabList, TabPanel, TabPanels, Tabs, Text, useColorModeValue } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { lazy, Suspense, useMemo, useState } from "react";
import { MessageConversation } from "src/components/Messages/MessageConversation";
import { TrackedTextarea } from "src/components/Survey/TrackedTextarea";
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";
import { TaskSurveyProps } from "src/components/Tasks/Task";
import { TaskHeader } from "src/components/Tasks/TaskHeader";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { TaskType } from "src/types/Task";
import { CreateTaskReply } from "src/types/TaskResponses";
import { CreateTaskType } from "src/types/Tasks";

const RenderedMarkdown = lazy(() => import("../Messages/RenderedMarkdown"));

export const CreateTask = ({
  task,
  taskType,
  isEditable,
  isDisabled,
  onReplyChanged,
  onValidityChanged,
}: TaskSurveyProps<CreateTaskType, CreateTaskReply>) => {
  const { t, i18n } = useTranslation(["tasks", "common"]);
  const cardColor = useColorModeValue("gray.50", "gray.800");
  const titleColor = useColorModeValue("gray.800", "gray.300");
  const [inputText, setInputText] = useState("");

  const textChangeHandler = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = event.target.value;
    onReplyChanged({ text });
    const isTextBlank = !text || /^\s*$/.test(text);
    if (!isTextBlank) {
      onValidityChanged("VALID");
      setInputText(text);
    } else {
      onValidityChanged("INVALID");
      setInputText("");
    }
  };

  const previewContent = useMemo(
    () => (
      <Suspense fallback={inputText}>
        <RenderedMarkdown markdown={inputText}></RenderedMarkdown>
      </Suspense>
    ),
    [inputText]
  );

  return (
    <div data-cy="task" data-task-type="create-task">
      <TwoColumnsWithCards>
        <>
          <TaskHeader taskType={taskType} />
          {task.type !== TaskType.initial_prompt && (
            <Box mt="4" borderRadius="lg" bg={cardColor} className="p-3 sm:p-6">
              <MessageConversation messages={task.conversation.messages} highlightLastMessage />
            </Box>
          )}
        </>
        <>
          <Stack spacing="4">
            {!!i18n.exists(`tasks:${taskType.id}.instruction`) && (
              <Text fontSize="xl" fontWeight="bold" color={titleColor}>
                {t(getTypeSafei18nKey(`tasks:${taskType.id}.instruction`))}
              </Text>
            )}
            {!isEditable ? (
              previewContent
            ) : (
              <Tabs isLazy>
                <TabList>
                  <Tab>{t("tab_write")}</Tab>
                  <Tab>{t("tab_preview")}</Tab>
                </TabList>
                <TabPanels>
                  <TabPanel p="0" pt="4">
                    <TrackedTextarea
                      text={inputText}
                      onTextChange={textChangeHandler}
                      thresholds={{ low: 20, medium: 40, goal: 50 }}
                      textareaProps={{
                        placeholder: t(getTypeSafei18nKey(`tasks:${taskType.id}.response_placeholder`)),
                        isDisabled,
                        minRows: 5,
                      }}
                    />
                  </TabPanel>
                  <TabPanel p="0" pt="4">
                    {previewContent}
                  </TabPanel>
                </TabPanels>
              </Tabs>
            )}
          </Stack>
        </>
      </TwoColumnsWithCards>
    </div>
  );
};
