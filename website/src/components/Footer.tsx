import { Box, Divider, Flex, Text, useColorMode } from "@chakra-ui/react";
import Image from "next/image";
import Link from "next/link";
import { useMemo } from "react";

export function Footer() {
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
                Open Assistant
              </Text>
              <Text fontSize="sm" color="gray.500">
                Conversational AI for everyone.
              </Text>
            </Box>
          </Flex>

          <nav>
            <Box display="flex" flexDirection={["column", "row"]} gap={["6", "14"]} alignItems="center" fontSize="sm">
              <Flex direction="column" alignItems={["center", "start"]}>
                <Text fontWeight="bold" color={textColor}>
                  Legal
                </Text>
                <FooterLink href="/privacy-policy" label="Privacy Policy" />
                <FooterLink href="/terms-of-service" label="Terms of Service" />
              </Flex>
              <Flex direction="column" alignItems={["center", "start"]}>
                <Text fontWeight="bold" color={textColor}>
                  Connect
                </Text>
                <FooterLink href="https://github.com/LAION-AI/Open-Assistant" label="Github" />
                <FooterLink href="https://ykilcher.com/open-assistant-discord" label="Discord" />
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
