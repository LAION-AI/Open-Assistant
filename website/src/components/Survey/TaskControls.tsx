import { Box, Flex, useColorModeValue } from "@chakra-ui/react";
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
        <SkipButton onSkip={props.onSkip} />
        <SubmitButton
          colorScheme="blue"
          data-cy="submit"
          disabled={props.taskStatus === "NOT_SUBMITTABLE" || props.taskStatus === "SUBMITTED"}
          onClick={props.onSubmit}
        >
          Submit
        </SubmitButton>
      </Flex>
    </Box>
  );
};
