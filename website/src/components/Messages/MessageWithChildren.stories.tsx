import { Story } from "@storybook/react";
import { rest } from "msw";
import { SessionProvider } from "next-auth/react";

import { MessageWithChildren, MessageWithChildrenProps } from "./MessageWithChildren";

// eslint-disable-next-line import/no-anonymous-default-export
export default {
  title: "Messages/MessageWithChildren",
  component: MessageWithChildren,
  parameters: {
    layout: "fullscreen",
    msw: {
      handlers: {
        messagesDefault: [
          rest.get("/api/messages/id-1", (req, res, ctx) => {
            return res(
              ctx.json({
                text: "Some message Text",
                is_assistant: false,
                id: "id-1",
              })
            );
          }),
          rest.get("/api/messages/id-1/children", (req, res, ctx) => {
            return res(ctx.json([]));
          }),
        ],
      },
    },
  },
};

const Template: Story<MessageWithChildrenProps> = (args) => (
  <SessionProvider>
    <MessageWithChildren {...args} />;
  </SessionProvider>
);

export const NoChildren = Template.bind({});
NoChildren.args = {
  id: "id-1",
  maxDepth: 2,
};

export const WithChildren = Template.bind({});
WithChildren.args = {
  id: "id-1",
  maxDepth: 1,
};
WithChildren.parameters = {
  msw: {
    handlers: {
      additionalMessages: [
        rest.get("/api/messages/id-2", (req, res, ctx) => {
          return res(
            ctx.json({
              text: "Some child message Text",
              is_assistant: false,
              id: "id-2",
            })
          );
        }),
        rest.get("/api/messages/id-3", (req, res, ctx) => {
          return res(
            ctx.json({
              text: "Some child message Text",
              is_assistant: false,
              id: "id-3",
            })
          );
        }),
        rest.get("/api/messages/id-1/children", (req, res, ctx) => {
          return res(
            ctx.json([
              {
                text: "Some child message Text",
                is_assistant: false,
                id: "id-2",
              },
              {
                text: "another child message Text",
                is_assistant: false,
                id: "id-3",
              },
            ])
          );
        }),
        rest.get("/api/messages/id-2/children", (req, res, ctx) => {
          return res(
            ctx.json([
              {
                text: "another message Text",
                is_assistant: false,
                id: "id-4",
              },
            ])
          );
        }),
        rest.get("/api/messages/id-3/children", (req, res, ctx) => {
          return res(ctx.json([]));
        }),
      ],
    },
  },
};
