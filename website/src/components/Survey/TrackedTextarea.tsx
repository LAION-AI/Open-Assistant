import { Progress, Stack, Textarea, TextareaProps } from "@chakra-ui/react";

interface TrackedTextboxProps {
  text: string;
  thresholds: {
    low: number;
    medium: number;
    goal: number;
  };
  textareaProps?: TextareaProps;
  onTextChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => void;
}

export const TrackedTextarea = (props: TrackedTextboxProps) => {
  const wordCount = (props.text.match(/\w+/g) || []).length;

  let progressColor: string;
  switch (true) {
    case wordCount < props.thresholds.low:
      progressColor = "red";
      break;
    case wordCount < props.thresholds.medium:
      progressColor = "yellow";
      break;
    default:
      progressColor = "green";
  }

  return (
    <Stack direction={"column"}>
      <Textarea data-cy="reply" value={props.text} onChange={props.onTextChange} {...props.textareaProps} />
      <Progress size={"md"} rounded={"md"} value={wordCount} colorScheme={progressColor} max={props.thresholds.goal} />
    </Stack>
  );
};
