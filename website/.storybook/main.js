const path = require("path");

module.exports = {
  stories: [
    "../src/components/**/*.stories.mdx",
    "../src/components/**/*.stories.@(js|jsx|ts|tsx)",
  ],
  addons: [
    "@storybook/addon-links",
    "@storybook/addon-essentials",
    "@storybook/addon-interactions",
    "@chakra-ui/storybook-addon",
  ],
  framework: "@storybook/react",
  core: {
    builder: "@storybook/builder-webpack5",
  },
  staticDirs: ["../public"],
  // https://github.com/storybookjs/storybook/issues/15336#issuecomment-888528747
  typescript: { reactDocgen: false },
  // fix to make absolute imports working in storybook
  webpackFinal: async (config, { configType }) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      src: path.resolve(__dirname, "../src"),
    };
    return config;
  },
  features: {
    emotionAlias: false,
  },
};
