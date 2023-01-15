import { Box, Divider } from "@chakra-ui/react";
import Image from "next/image";
import Link from "next/link";
import { useMemo } from "react";

export function Footer() {
  return (
    <footer>
      <Divider />
      <Box display="flex" gap="4" flexDir="column" alignItems="center" mt="10">
        <Box display="flex" alignItems="center">
          <Link href="/" aria-label="Home" className="flex items-center">
            <Image src="/images/logos/logo.svg" className="mx-auto object-fill" width="48" height="48" alt="logo" />
          </Link>
        </Box>
        <nav>
          <Box display="flex" gap="5" fontSize="xs" color="blue.500">
            <FooterLink href="/privacy-policy" label="Privacy Policy" />
            <FooterLink href="/terms-of-service" label="Terms of Service" />
            <FooterLink href="https://github.com/LAION-AI/Open-Assistant" label="Github" />
            <FooterLink href="https://ykilcher.com/open-assistant-discord" label="Discord" />
          </Box>
        </nav>
      </Box>
    </footer>
  );
}

const FooterLink = ({ href, label }: { href: string; label: string }) =>
  useMemo(
    () => (
      <Link
        href={href}
        rel="noopener noreferrer nofollow"
        target="_blank"
        aria-label={label}
        className="hover:underline underline-offset-2"
      >
        {label}
      </Link>
    ),
    [href, label]
  );
