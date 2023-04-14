import { Box, Link, Text, useColorMode } from "@chakra-ui/react";
import { SiDiscord, SiGithub } from "@icons-pack/react-simple-icons";
import { Users } from "lucide-react";
import { useTranslation } from "next-i18next";
import { useId } from "react";

import { Container } from "./Container";

const CIRCLE_HEIGHT = 558;
const CIRCLE_WIDTH = 558;

function CircleBackground() {
  const id = useId();

  const { colorMode } = useColorMode();
  const baseRingColor = colorMode === "light" ? "#777" : "#000";
  const gradStopColor = colorMode === "light" ? "#fff" : "#000";

  return (
    <svg
      viewBox={`0 0 ${CIRCLE_HEIGHT} ${CIRCLE_WIDTH}`}
      width={CIRCLE_WIDTH}
      height={CIRCLE_HEIGHT}
      fill="none"
      aria-hidden="true"
      className="animate-spin-slower"
    >
      <defs>
        <linearGradient id={id} x1="79" y1="16" x2="105" y2="237" gradientUnits="userSpaceOnUse">
          <stop stopColor={gradStopColor} />
          <stop offset="1" stopColor={baseRingColor} stopOpacity="0" />
        </linearGradient>
      </defs>
      <path
        opacity=".2"
        d="M1 279C1 125.465 125.465 1 279 1s278 124.465 278 278-124.465 278-278 278S1 432.535 1 279Z"
        stroke={baseRingColor}
      />
      <path d="M1 279C1 125.465 125.465 1 279 1" stroke={`url(#${id})`} strokeLinecap="round" />
    </svg>
  );
}

export function CallToAction() {
  const { colorMode } = useColorMode();
  const { t } = useTranslation();
  const bgColorClass = colorMode === "light" ? "bg-gray-900" : "bg-gray-50";
  const headingColorClass = colorMode === "light" ? "text-white" : "text-black";
  const textColorClass = colorMode === "light" ? "text-gray-300" : "text-black";

  return (
    <Box
      as="section"
      id="join-us"
      className={`relative overflow-hidden py-20 sm:py-28 ${bgColorClass} ${textColorClass}`}
    >
      <Box className="absolute top-1/2 left-20 -translate-y-1/2 sm:left-1/2 sm:-translate-x-1/2">
        <CircleBackground />
      </Box>
      <Container className="relative">
        <Box className="mx-auto max-w-md sm:text-center">
          <Text as="h2" className={`text-3xl font-medium tracking-tight sm:text-4xl ${headingColorClass}`}>
            {t("index:join_us_title")}
          </Text>

          <Text as="p" className="mt-4 text-lg">
            {t("index:join_us_description")}
          </Text>

          <Box className="mt-8 flex justify-center" gap={["2", "4"]}>
            <Link href="https://ykilcher.com/open-assistant-discord" rel="noreferrer" target="_blank">
              <button
                type="button"
                className="mb-2 flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-3 text-base font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                <SiDiscord size={20} />
                <Text as="span" className="ml-3" fontSize={["sm", "md", "lg"]}>
                  {t("discord")}
                </Text>
              </button>
            </Link>
            <Link href="https://github.com/LAION-AI/Open-Assistant" rel="noreferrer" target="_blank">
              <button
                type="button"
                className="mb-2 flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-3 text-base font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                <SiGithub size={20} />
                <Text as="span" className="ml-3" fontSize={["sm", "md", "lg"]}>
                  {t("github")}
                </Text>
              </button>
            </Link>
            <Link href="/team" rel="noreferrer" target="_blank">
              <button
                type="button"
                className="mb-2 flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-3 text-base font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                <Users size={20} />
                <Text as="span" className="ml-3" fontSize={["sm", "md", "lg"]}>
                  {t("team")}
                </Text>
              </button>
            </Link>
          </Box>
        </Box>
      </Container>
    </Box>
  );
}
