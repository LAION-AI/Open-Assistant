const path = require("path");

module.exports = {
  stories: ["../src/components/**/*.stories.mdx", "../src/components/**/*.stories.@(js|jsx|ts|tsx)"],
  addons: [
    "@storybook/addon-links",
    "@storybook/addon-essentials",
    "@storybook/addon-interactions",
    "@chakra-ui/storybook-addon",
  ],
  framework: "@storybook/nextjs",
  staticDirs: ["../public"],
  // https://github.com/storybookjs/storybook/issues/15336#issuecomment-888528747
  typescript: { reactDocgen: false },
  // https://github.com/i18next/next-i18next/issues/1012
  webpackFinal: async (config) => {
    config.resolve.fallback = {
      fs: false,
      path: require.resolve("path-browserify"),
    };
    return config;
  },
  features: {
    emotionAlias: false,
  },
};
