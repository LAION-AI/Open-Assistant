import { Box, Divider } from "@chakra-ui/react";
import Image from "next/image";
import Link from "next/link";
import { useTranslation } from "next-i18next";
import { useMemo } from "react";

export function SlimFooter() {
  const { t } = useTranslation();
  return (
    <footer>
      <Box>
        <Divider />
        <Box display="flex" gap="4" flexDir="column" alignItems="center" my="8">
          <Box display="flex" alignItems="center">
            <Link href="/" aria-label="Home" className="flex items-center gap-1">
              <Image src="/images/logos/logo.svg" className="mx-auto object-fill" width="48" height="48" alt="logo" />
            </Link>
          </Box>
          <nav>
            <Box display="flex" gap="5" fontSize="xs" color="blue.500">
              <FooterLink href="/privacy-policy" label={t("privacy_policy")} />
              <FooterLink href="/terms-of-service" label={t("terms_of_service")} />
              <FooterLink href="https://github.com/LAION-AI/Open-Assistant" label={t("github")} />
              <FooterLink href="https://ykilcher.com/open-assistant-discord" label={t("discord")} />
              <FooterLink href="https://projects.laion.ai/Open-Assistant/" label={t("docs")} />
              <FooterLink href="https://projects.laion.ai/Open-Assistant/docs/faq" label={t("faq")} />
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
