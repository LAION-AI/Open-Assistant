import { SessionContext } from "next-auth/react";
import React from "react";
import { FlagsProvider } from "react-feature-flags";

import { RouterDecorator } from "../../../.storybook/decorators";
import { Header } from "./Header";

// eslint-disable-next-line import/no-anonymous-default-export
export default {
  title: "Header/Header",
  component: Header,
  parameters: {
    layout: "fullscreen",
  },
  decorators: [RouterDecorator],
};

const Template = (args) => {
  var { session } = args;
  return (
    <SessionContext.Provider value={session}>
      <FlagsProvider value={[{ name: "flagTest", isActive: false }]}>
        <Header {...args} />
      </FlagsProvider>
    </SessionContext.Provider>
  );
};

export const Default = Template.bind({});
Default.args = {
  session: {
    data: {
      user: {
        name: "StoryBook user",
      },
    },
    status: "authenticated",
  },
  transparent: false,
  borderClass: undefined,
};
