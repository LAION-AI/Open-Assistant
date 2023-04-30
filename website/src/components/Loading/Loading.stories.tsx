import type { ComponentStory } from "@storybook/react";

import { LoadingScreen } from "./LoadingScreen";

// eslint-disable-next-line import/no-anonymous-default-export
export default {
  title: "Example/LoadingScreen",
  component: LoadingScreen,
  parameters: {
    layout: "fullscreen",
  },
};

const Template: ComponentStory<typeof LoadingScreen> = (args) => <LoadingScreen {...args} />;

export const Default = Template.bind({});

export const WithText = Template.bind({});
WithText.args = { text: "Loading Text ..." };
