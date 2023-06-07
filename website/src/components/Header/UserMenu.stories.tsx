import type { ComponentStory } from "@storybook/react";
import { SessionContext } from "next-auth/react";
import React from "react";

import UserMenu from "./UserMenu";

// eslint-disable-next-line import/no-anonymous-default-export
export default {
  title: "Header/UserMenu",
  component: UserMenu,
};

const Template: ComponentStory<any> = (args) => {
  const { session } = args;
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
