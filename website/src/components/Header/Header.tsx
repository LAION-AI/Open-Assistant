import { Box, Button, Flex, Text } from "@chakra-ui/react";
import { Show } from "@chakra-ui/react";
import { User } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { useTranslation } from "next-i18next";
import { ReactNode } from "react";
import { LanguageSelector } from "src/components/LanguageSelector";

import { ColorModeToggler } from "./ColorModeToggler";
import { UserMenu } from "./UserMenu";
import { UserScore } from "./UserScore";

function AccountButton() {
  const { data: session } = useSession();
  if (session) {
    return null;
  }
  return (
    <Link href="/auth/signin" aria-label="Home">
      <Flex alignItems="center">
        <Button variant="outline" leftIcon={<User size={"20"} />}>
          Sign in
        </Button>
      </Flex>
    </Link>
  );
}

export const HEADER_HEIGHT = "82px";

export function Header() {
  const { t } = useTranslation();
  const { data: session } = useSession();
  const homeURL = session ? "/dashboard" : "/";

  return (
    <Box
      as="header"
      className="oa-basic-theme"
      display="flex"
      justifyContent="space-between"
      p="4"
      position="fixed"
      zIndex={20}
      w="full"
      height={HEADER_HEIGHT}
      shadow="md"
    >
      <Link href={homeURL} aria-label="Home">
        <Flex alignItems="center">
          <Image src="/images/logos/logo.svg" className="mx-auto object-fill" width="50" height="50" alt="logo" />
          <Text fontFamily="inter" fontSize={["lg", "2xl"]} fontWeight="bold" ml="3" className="hidden sm:block">
            {t("title")}
          </Text>
        </Flex>
      </Link>

      <Flex alignItems="center" gap={["2", "4"]}>
        <LanguageSelector />
        <AccountButton />
        <UserMenu />
        <Show above="md">
          <UserScore />
        </Show>
        <ColorModeToggler />
      </Flex>
    </Box>
  );
}

export const HeaderLayout = ({ children }: { children: ReactNode }) => {
  return (
    <>
      <Header></Header>
      <Box paddingTop={HEADER_HEIGHT} minH={`calc(100vh - ${HEADER_HEIGHT})`} h="full">
        {children}
      </Box>
    </>
  );
};
