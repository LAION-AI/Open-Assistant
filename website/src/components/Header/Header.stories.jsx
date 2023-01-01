import { SessionContext } from "next-auth/react";
import React from "react";

import { Header } from "./Header";

// eslint-disable-next-line import/no-anonymous-default-export
export default {
  title: "Header/Header",
  component: Header,
  parameters: {
    layout: "fullscreen",
  },
};

const Template = (args) => {
  var { session } = args;
  return (
    <SessionContext.Provider value={session}>
      <Header {...args} />
    </SessionContext.Provider>
  );
};

export const Default = Template.bind({});
Default.args = { session: { data: { user: { name: "StoryBook user" } }, status: "authenticated" }, transparent: false };
