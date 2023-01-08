// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require("prism-react-renderer/themes/github");
const darkCodeTheme = require("prism-react-renderer/themes/dracula");

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "Open Assistant",
  tagline: "Build the assistant of the future!",
  url: "https://LAION-AI.github.io",
  trailingSlash: false,
  baseUrl: "/Open-Assistant/",
  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",
  favicon: "img/logo.svg",
  staticDirectories: ["public", "static", "docs/data/img"],

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: "LAION-AI", // Usually your GitHub org/user name.
  projectName: "Open-Assistant", // Usually your repo name.
  deploymentBranch: "main",

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  presets: [
    [
      "classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve("./sidebars.js"),
        },
        blog: false,
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: "Open Assistant",
        logo: {
          alt: "Open Assistant Logo",
          src: "img/logo.svg",
        },
        items: [
          {
            type: "doc",
            docId: "intro",
            position: "left",
            label: "Docs",
          },
          //{ to: "/blog", label: "Blog", position: "left" },
          {
            href: "https://github.com/LAION-AI/Open-Assistant",
            label: "GitHub",
            position: "right",
          },
        ],
      },
      footer: {
        style: "dark",
        links: [
          {
            title: "Community",
            items: [
              {
                label: "OpenAssistant Contributors Discord",
                href: "https://ykilcher.com/open-assistant-discord",
              },
              {
                label: "LAION Discord",
                href: "https://discord.com/invite/mVcgxMPD7e",
              },
              {
                label: "YK Discord",
                href: "https://ykilcher.com/discord",
              },
            ],
          },
          {
            title: "Resources",
            items: [
              {
                label: "GitHub",
                href: "https://github.com/LAION-AI/Open-Assistant",
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} laion.ai. Built with Docusaurus.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
      },
    }),
};

module.exports = config;
