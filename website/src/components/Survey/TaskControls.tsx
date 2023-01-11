import { useColorMode } from "@chakra-ui/react";
import { Flex } from "@chakra-ui/react";
import clsx from "clsx";
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
  onNextTask: () => void;
}

export const TaskControls = (props: TaskControlsProps) => {
  const { colorMode } = useColorMode();
  const isLightMode = colorMode === "light";
  return (
    <section
      className={clsx(
        "flex-row justify-items-stretch mb-8 p-4 rounded-lg max-w-7xl mx-auto space-y-4 sm:space-y-0 sm:flex",
        props.className,
        {
          "bg-white text-gray-800 shadow-lg": isLightMode,
          "bg-slate-800 text-slate-400 shadow-xl ring-1 ring-white/10 ring-inset": !isLightMode,
        }
      )}
    >
      <TaskInfo id={props.task.id} output="Submit your answer" />
      <Flex justify="center" ml="auto" gap={2}>
        <SkipButton onSkip={props.onSkip} disabled={props.taskStatus === "SUBMITTED"} />
        {props.taskStatus !== "SUBMITTED" ? (
          <SubmitButton
            colorScheme="blue"
            data-cy="submit"
            disabled={props.taskStatus === "NOT_SUBMITTABLE"}
            onClick={props.onSubmit}
          >
            Submit
          </SubmitButton>
        ) : (
          <SubmitButton colorScheme="green" data-cy="next-task" onClick={props.onNextTask}>
            Next Task
          </SubmitButton>
        )}
      </Flex>
    </section>
  );
};
