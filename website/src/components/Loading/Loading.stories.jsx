import { LoadingScreen } from "./LoadingScreen";

export default {
  title: "Example/LoadingScreen",
  component: LoadingScreen,
  parameters: {
    layout: "fullscreen",
  },
};

const Template = (args) => <LoadingScreen {...args} />; //<><div>text</div><div className="max-w-500 mt-40 z-1000 h-full relative"></div></>;

export const Default = Template.bind({});

export const WithText = Template.bind({});
WithText.args = { text: "Loading Text ..." };
