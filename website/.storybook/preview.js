import "!style-loader!css-loader!postcss-loader!tailwindcss/tailwind.css";
import { initialize, mswDecorator } from "msw-storybook-addon";
import { rest } from "msw";

// Initialize MSW
initialize();

// Provide the MSW addon decorator globally
export const decorators = [mswDecorator];

export const parameters = {
  actions: { argTypesRegex: "^on[A-Z].*" },
  controls: {
    matchers: {
      color: /(background|color)$/i,
      date: /Date$/,
    },
  },
  msw: {
    handlers: {
      labels: [
        rest.get("/api/valid_labels", (req, res, ctx) => {
          return res(
            ctx.json({
              valid_labels: [
                {
                  name: "spam",
                  display_text:
                    "Seems to be intentionally low-quality or irrelevant",
                  help_text: null,
                },
                {
                  name: "fails_task",
                  display_text:
                    "Fails to follow the correct instruction / task",
                  help_text: null,
                },
                {
                  name: "not_appropriate",
                  display_text: "Inappropriate for customer assistant",
                  help_text: null,
                },
                {
                  name: "violence",
                  display_text:
                    "Encourages or fails to discourage violence/abuse/terrorism/self-harm",
                  help_text: null,
                },
              ],
            })
          );
        }),
      ],
    },
  },
};

// Hacky solution to get Images in next to work
// https://dev.to/jonasmerlin/how-to-use-the-next-js-image-component-in-storybook-1415
import * as NextImage from "next/image";

const OriginalNextImage = NextImage.default;

Object.defineProperty(NextImage, "default", {
  configurable: true,
  value: (props) => <OriginalNextImage {...props} unoptimized />,
});
