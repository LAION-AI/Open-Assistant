import { SessionContext } from 'next-auth/react';
import React from 'react';

import { Header } from './Header';

export default {
  title: 'Example/Header',
  component: Header,
  parameters: {
    // More on Story layout: https://storybook.js.org/docs/react/configure/story-layout
    layout: 'fullscreen',
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
Default.args =  {session :{ data: {user: { name: "StoryBook user"}}, status: "authenticated",  }};
