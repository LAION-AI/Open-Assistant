import { Box, Divider, Flex, Text, useColorMode } from "@chakra-ui/react";
import Image from "next/image";
import Link from "next/link";
import { useTranslation } from "next-i18next";
import { useMemo } from "react";

export function Footer() {
  const { t } = useTranslation();
  const { colorMode } = useColorMode();
  const backgroundColor = colorMode === "light" ? "white" : "gray.800";
  const textColor = colorMode === "light" ? "black" : "gray.300";

  return (
    <footer>
      <Box bg={backgroundColor}>
        <Divider />
        <Box
          display="flex"
          flexDirection={["column", "row"]}
          justifyContent="space-between"
          alignItems="center"
          gap="6"
          p="8"
          pb={["14", "8"]}
          w="full"
          mx="auto"
          maxWidth="7xl"
        >
          <Flex alignItems="center">
            <Box pr="2">
              <Link href="/" aria-label="Home">
                <Image src="/images/logos/logo.svg" width="52" height="52" alt="logo" />
              </Link>
            </Box>

            <Box>
              <Text fontSize="md" fontWeight="bold">
                {t("title")}
              </Text>
              <Text fontSize="sm" color="gray.500">
                {t("conversational")}
              </Text>
            </Box>
          </Flex>

          <nav>
            <Box display="flex" flexDirection={["column", "row"]} gap={["6", "14"]} fontSize="sm">
              <Flex direction="column" alignItems={["center", "start"]}>
                <Text fontWeight="bold" color={textColor}>
                  {t("legal")}
                </Text>
                <FooterLink href="/privacy-policy" label={t("privacy_policy")} />
                <FooterLink href="/terms-of-service" label={t("terms_of_service")} />
              </Flex>
              <Flex direction="column" alignItems={["center", "start"]}>
                <Text fontWeight="bold" color={textColor}>
                  {t("connect")}
                </Text>
                <FooterLink href="https://github.com/LAION-AI/Open-Assistant" label={t("github")} />
                <FooterLink href="https://ykilcher.com/open-assistant-discord" label={t("discord")} />
              </Flex>
              <Flex direction="column" alignItems={["center", "start"]}>
                <Text fontWeight="bold" color={textColor}>
                  {t("about")}
                </Text>
                <FooterLink href="https://projects.laion.ai/Open-Assistant" label={t("docs")} />
                <FooterLink href="https://projects.laion.ai/Open-Assistant/docs/faq" label={t("faq")} />
              </Flex>
            </Box>
          </nav>
        </Box>
      </Box>
    </footer>
  );
}

const FooterLink = ({ href, label }: { href: string; label: string }) =>
  useMemo(
    () => (
      <Link href={href} rel="noopener noreferrer nofollow" target="_blank" aria-label={label}>
        <Text color="blue.500" textUnderlineOffset={2} _hover={{ textDecoration: "underline" }}>
          {label}
        </Text>
      </Link>
    ),
    [href, label]
  );
