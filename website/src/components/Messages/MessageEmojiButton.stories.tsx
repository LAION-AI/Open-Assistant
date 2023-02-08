import React from "react";

import { MessageEmojiButton } from "./MessageEmojiButton";

// eslint-disable-next-line import/no-anonymous-default-export
export default {
  title: "Messages/MessageEmojiButton",
  component: MessageEmojiButton,
};

const Template = ({
  emoji,
  count,
  checked,
  showCount,
}: {
  emoji: string;
  count: number;
  checked?: boolean;
  showCount: boolean;
}) => {
  return (
    <MessageEmojiButton emoji={{ name: emoji, count }} checked={checked} onClick={undefined} showCount={showCount} />
  );
};

export const Default = Template.bind({});
Default.args = {
  emoji: "+1",
  count: 7,
  checked: false,
  showCount: true,
};

export const BigNumber = Template.bind({});
BigNumber.args = {
  emoji: "+1",
  count: 999,
  checked: false,
  showCount: true,
};

export const Checked = Template.bind({});
Checked.args = {
  emoji: "+1",
  count: 2,
  checked: true,
  showCount: true,
};
