import { ComponentMeta } from "@storybook/react";

import { LikertButtons } from "./LikertButtons";
import { SkipButton } from "./Skip";
import { SubmitButton } from "./Submit";

export default {
  title: "Buttons",
} as ComponentMeta<typeof SubmitButton>;

export const Submit = () => <SubmitButton>Submit</SubmitButton>;

export const Likert = () => {
  return (
    <LikertButtons
      isDisabled={false}
      count={3}
      data-cy="label-options"
      onChange={() => console.log("onChange")}
    ></LikertButtons>
  );
};

export const Skip = () => <SkipButton onSkip={() => console.log("onClick")}>Skip</SkipButton>;
