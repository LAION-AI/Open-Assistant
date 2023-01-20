import { Box, useColorMode } from "@chakra-ui/react";
import React, { useId } from "react";

export const AnimatedCircles = () => {
  const id = useId();
  const { colorMode } = useColorMode();
  const baseRingColor = colorMode === "light" ? "#d4d4d4" : "#005a69";
  const gradStopColor = colorMode === "light" ? "#06b6d4" : "#00f2ff";

  return (
    <Box className="absolute left-1/2 top-4 h-[1026px] w-[1026px] -translate-x-1/3 stroke-gray-300/70 [mask-image:linear-gradient(to_bottom,white_20%,transparent_75%)] sm:top-16 sm:-translate-x-1/2 lg:-top-16 lg:ml-12 xl:-top-14 xl:ml-0">
      <svg
        viewBox="0 0 1026 1026"
        fill="none"
        aria-hidden="true"
        className="absolute inset-0 h-full w-full animate-spin-slow"
      >
        <path
          d="M1025 513c0 282.77-229.23 512-512 512S1 795.77 1 513 230.23 1 513 1s512 229.23 512 512Z"
          stroke={baseRingColor}
          strokeOpacity="0.7"
        />
        <path d="M513 1025C230.23 1025 1 795.77 1 513" stroke={`url(#${id}-gradient-1)`} strokeLinecap="round" />
        <defs>
          <linearGradient id={`${id}-gradient-1`} x1="1" y1="513" x2="1" y2="1025" gradientUnits="userSpaceOnUse">
            <stop stopColor={gradStopColor} />
            <stop offset="1" stopColor={gradStopColor} stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>
      <svg
        viewBox="0 0 1026 1026"
        fill="none"
        aria-hidden="true"
        className="absolute inset-0 h-full w-full animate-spin-reverse-slower"
      >
        <path
          d="M913 513c0 220.914-179.086 400-400 400S113 733.914 113 513s179.086-400 400-400 400 179.086 400 400Z"
          stroke={baseRingColor}
          strokeOpacity="0.7"
        />
        <path d="M913 513c0 220.914-179.086 400-400 400" stroke={`url(#${id}-gradient-2)`} strokeLinecap="round" />
        <defs>
          <linearGradient id={`gradient-2`} x1="913" y1="513" x2="913" y2="913" gradientUnits="userSpaceOnUse">
            <stop stopColor={gradStopColor} />
            <stop offset="1" stopColor={gradStopColor} stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>
    </Box>
  );
};
