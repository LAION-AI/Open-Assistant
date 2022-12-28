import "!style-loader!css-loader!postcss-loader!tailwindcss/tailwind.css";

export const parameters = {
  actions: { argTypesRegex: "^on[A-Z].*" },
  controls: {
    matchers: {
      color: /(background|color)$/i,
      date: /Date$/,
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
