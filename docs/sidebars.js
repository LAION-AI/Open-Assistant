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
        type: "doc",
        id: "guides/README",
      },
      items: ["guides/guidelines", "guides/examples", "guides/developers"],
    },
    {
      type: "category",
      label: "Tasks",
      link: {
        type: "doc",
        id: "tasks/README",
      },
      items: [
        "tasks/label_assistant_reply",
        "tasks/label_prompter_reply",
        "tasks/reply_as_assistant",
        "tasks/reply_as_user",
        "tasks/rank_assistant_replies",
      ],
    },
    {
      type: "category",
      label: "Data",
      link: {
        type: "doc",
        id: "data/README",
      },
      items: [
        "data/schemas",
        "data/datasets",
        "data/augmentation",
        "data/supervised-datasets",
      ],
    },
    {
      type: "category",
      label: "Research",
      link: {
        type: "doc",
        id: "research/README",
      },
      items: ["research/general", "research/search-based-qa"],
    },
    {
      type: "category",
      label: "Presentations",
      link: {
        type: "doc",
        id: "presentations/README",
      },
      items: ["presentations/list"],
    },
    {
      type: "doc",
      label: "FAQ",
      id: "faq",
    },
  ],
};

module.exports = sidebars;
