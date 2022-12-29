import { SessionContext } from "next-auth/react";
import React from "react";

import UserMenu from "./UserMenu";

export default {
  title: "Header/UserMenu",
  component: UserMenu,
};

const Template = (args) => {
  var { session } = args;
  return (
    <SessionContext.Provider value={session}>
      <div className="flex flex-col">
        <div className="self-end">
          <UserMenu {...args} />
        </div>
      </div>
    </SessionContext.Provider>
  );
};

export const Default = Template.bind({});
Default.args = { session: { data: { user: { name: "StoryBook user" } }, status: "authenticated" } };
