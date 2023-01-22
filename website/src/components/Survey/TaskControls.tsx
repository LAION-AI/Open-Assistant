import { Box, Flex, IconButton, Tooltip, useColorModeValue } from "@chakra-ui/react";
import { Edit2 } from "lucide-react";
import { SkipButton } from "src/components/Buttons/Skip";
import { SubmitButton } from "src/components/Buttons/Submit";
import { TaskInfo } from "src/components/TaskInfo/TaskInfo";
import { TaskStatus } from "src/components/Tasks/Task";

export interface TaskControlsProps {
  // we need a task type
  // eslint-disable-next-line  @typescript-eslint/no-explicit-any
  task: any;
  className?: string;
  taskStatus: TaskStatus;
  onEdit: () => void;
  onReview: () => void;
  onSubmit: () => void;
  onSkip: (reason: string) => void;
}

export const TaskControls = (props: TaskControlsProps) => {
  const backgroundColor = useColorModeValue("white", "gray.800");

  return (
    <Box
      width="full"
      bg={backgroundColor}
      borderRadius="xl"
      p="6"
      display="flex"
      flexDirection={["column", "row"]}
      shadow="base"
      gap="4"
    >
      <TaskInfo id={props.task.id} output="Submit your answer" />
      <Flex width={["full", "fit-content"]} justify="center" ml="auto" gap={2}>
        {props.taskStatus === "REVIEW" || props.taskStatus === "SUBMITTED" ? (
          <>
            <Tooltip label="Edit">
              <IconButton
                size="lg"
                data-cy="edit"
                aria-label="edit"
                onClick={props.onEdit}
                icon={<Edit2 size="1em" />}
              />
            </Tooltip>
            <SubmitButton
              colorScheme="green"
              data-cy="submit"
              disabled={props.taskStatus === "SUBMITTED"}
              onClick={props.onSubmit}
            >
              Submit
            </SubmitButton>
          </>
        ) : (
          <>
            <SkipButton onSkip={props.onSkip} />
            <SubmitButton
              colorScheme="blue"
              data-cy="review"
              disabled={props.taskStatus === "NOT_SUBMITTABLE"}
              onClick={props.onReview}
            >
              Review
            </SubmitButton>
          </>
        )}
      </Flex>
    </Box>
  );
};
