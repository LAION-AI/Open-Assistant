import { NavLinks } from "./NavLinks";

// eslint-disable-next-line import/no-anonymous-default-export
export default {
  title: "Header/NavLinks",
  component: NavLinks,
};

const Template = (args) => (
  <div className="hidden lg:flex lg:gap-10">
    <NavLinks {...args} />
  </div>
);

export const Default = Template.bind({});
