/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  sidebar: [
    "intro",
    {
      type: "category",
      label: "Guides",
      link: {
        type: "generated-index",
        description: "Useful guides.",
      },
      items: ["guides/prompting"],
    },
    {
      type: "category",
      label: "Data",
      link: {
        type: "generated-index",
        description: "Important data concepts.",
      },
      items: ["data/schemas", "data/augmentation", "data/supervised-datasets"],
    },
    {
      type: "category",
      label: "Research",
      link: {
        type: "generated-index",
        description: "Useful research material.",
      },
      items: ["research/general", "research/search-based-qa"],
    },
    {
      type: "category",
      label: "Presentations",
      link: {
        type: "generated-index",
        description: "Useful decks and presentations.",
      },
      items: ["presentations/presentations"],
    },
  ],
};

module.exports = sidebars;
