import { Story } from "@storybook/react";
import { SessionProvider } from "next-auth/react";
import React from "react";

import { MessageTableEntry } from "./MessageTableEntry";

// eslint-disable-next-line import/no-anonymous-default-export
export default {
  title: "Messages/MessageTableEntry",
  component: MessageTableEntry,
};

const Template: Story<any> = ({ enabled, highlight, ...message }) => {
  return (
    <SessionProvider>
      <MessageTableEntry message={message} enabled={enabled} highlight={highlight} />;
    </SessionProvider>
  );
};

export const Default = Template.bind({});
Default.args = {
  text: "Who were the 8 presidents before George Washington?",
  is_assistant: false,
  id: "",
  frontend_message_id: "",
  enabled: true,
  highlight: false,
  emojis: {},
  user_emojis: [],
};

export const Asistant = Template.bind({});
Asistant.args = {
  text: "Who were the 8 presidents before George Washington?",
  is_assistant: true,
  id: "",
  frontend_message_id: "",
  enabled: true,
  highlight: false,
  emojis: {},
  user_emojis: [],
};

export const LongText = Template.bind({});
LongText.args = {
  text: "Assistant: No.  The USA was founded by a Puritan group of Protestants, but it didn\u2019t adopt the religion of the Puritans until much later, and it was always a secular state.  The Puritans observed the Sabbath on Sunday, and the Puritans only had a small influence in the early history of the USA.  It\u2019s difficult to trace the origins of closing stores on Sunday, but one early and short-lived attempt at forcing the Sabbath on people in the 1800s was motivated by the Protestant ideal that people should spend Sunday focusing on spiritual activities.  By the mid-1800s, when the Sunday closing law was made, there was not a lot of pressure from that standpoint, but the church had begun to advocate for Sunday closing laws as a way of counteracting the negative effects of industrialization on the day of rest.  Even after that shift, closing stores on Sunday was not always possible, since the religious Sunday was not always chosen for observance.  And as industrialization accelerated and mechanization made it possible to operate stores on Sunday, the law was not enforced as much as people liked.  The day of rest was also being violated by stores that stayed open all day on Sunday, so closing stores on Sundays became an effort to protect the Sabbath for all citizens.",
  is_assistant: true,
  id: "",
  frontend_message_id: "",
  enabled: true,
  highlight: false,
  emojis: {},
  user_emojis: [],
};

export const WithEmoji = Template.bind({});
WithEmoji.args = {
  text: "As you\u2019ve mentioned, Star Wars has many sequels, prequels, and crossovers.  The official list of movies in Star Wars is:",
  is_assistant: true,
  id: "",
  frontend_message_id: "",
  enabled: true,
  highlight: false,
  emojis: { "-1": 5, "+1": 1 },
  user_emojis: ["-1"],
};
