import React from "react";

import { MessageEmojiButton } from "./MessageEmojiButton";

// eslint-disable-next-line import/no-anonymous-default-export
export default {
  title: "Messages/MessageEmojiButton",
  component: MessageEmojiButton,
};

const Template = ({ emoji, count, checked }: { emoji: string; count: number; checked?: boolean }) => {
  return <MessageEmojiButton emoji={{ name: emoji, count }} checked={checked} onClick={undefined} />;
};

export const Default = Template.bind({});
Default.args = {
  emoji: "+1",
  count: 7,
  checked: false,
};

export const BigNumber = Template.bind({});
BigNumber.args = {
  emoji: "+1",
  count: 999,
  checked: false,
};

export const Checked = Template.bind({});
Checked.args = {
  emoji: "+1",
  count: 2,
  checked: true,
};
