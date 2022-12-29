import { LoadingScreen } from "./LoadingScreen";

export default {
  title: "Example/LoadingScreen",
  component: LoadingScreen,
  parameters: {
    layout: "fullscreen",
  },
};

const Template = (args) => <LoadingScreen {...args} />;

export const Default = Template.bind({});

export const WithText = Template.bind({});
WithText.args = { text: "Loading Text ..." };
