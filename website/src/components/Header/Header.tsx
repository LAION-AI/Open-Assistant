import { Box, Button, Flex, Text } from "@chakra-ui/react";
import Image from "next/image";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { useTranslation } from "next-i18next";
import { Flags } from "react-feature-flags";
import { FaUser } from "react-icons/fa";
import { LanguageSelector } from "src/components/LanguageSelector";

import { UserMenu } from "./UserMenu";

function AccountButton() {
  const { data: session } = useSession();
  if (session) {
    return;
  }
  return (
    <Link href="/auth/signin" aria-label="Home">
      <Flex alignItems="center">
        <Button variant="outline" leftIcon={<FaUser />}>
          Sign in
        </Button>
      </Flex>
    </Link>
  );
}

export function Header() {
  const { t } = useTranslation();
  const { data: session } = useSession();
  const homeURL = session ? "/dashboard" : "/";

  return (
    <nav className="oa-basic-theme">
      <Box display="flex" justifyContent="space-between" p="4">
        <Link href={homeURL} aria-label="Home">
          <Flex alignItems="center">
            <Image src="/images/logos/logo.svg" className="mx-auto object-fill" width="50" height="50" alt="logo" />
            <Text fontFamily="inter" fontSize="2xl" fontWeight="bold" ml="3">
              {t("title")}
            </Text>
          </Flex>
        </Link>

        <Flex alignItems="center" gap="4">
          <Flags authorizedFlags={["flagTest"]}>
            <Text>FlagTest</Text>
          </Flags>
          <LanguageSelector />
          <AccountButton />
          <UserMenu />
        </Flex>
      </Box>
    </nav>
  );
}
