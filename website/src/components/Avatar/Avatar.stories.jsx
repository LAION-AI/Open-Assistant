import { SessionContext } from "next-auth/react";
import React from "react";

import { Avatar } from "./Avatar";

export default {
  title: "Example/Avatar",
  component: Avatar,
};

const Template = (args) => {
  var { session } = args;
  return (
    <SessionContext.Provider value={session}>
      <Avatar {...args} />
    </SessionContext.Provider>
  );
};

export const Default = Template.bind({});
Default.args = { session: { data: { user: { name: "StoryBook user" } }, status: "authenticated" } };
