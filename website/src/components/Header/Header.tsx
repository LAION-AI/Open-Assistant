import { Box, Divider, Button, Text, Flex, useColorMode } from "@chakra-ui/react";
import Image from "next/image";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { Flags } from "react-feature-flags";
import { FaUser } from "react-icons/fa";
import { colors } from "src/styles/Theme/colors";

import { UserMenu } from "./UserMenu";

function AccountButton() {
  const { data: session } = useSession();
  if (session) {
    return;
  }
  return (
    <Link href="/auth/signin" aria-label="Home" className="flex items-center">
      <Button variant="outline" leftIcon={<FaUser />}>
        Sign in
      </Button>
    </Link>
  );
}

export function Header(props) {
  const { data: session } = useSession();
  const homeURL = session ? "/dashboard" : "/";

  const { colorMode } = useColorMode();
  const borderClass = props.transparent
    ? ""
    : colorMode === "light"
    ? "border-b border-gray-400"
    : "border-b border-zinc-800";
  return (
    <nav className="oa-basic-theme">
      <Box position="relative" display="flex" z="10" justifyContent="space-between" p="4">
        <Link href={homeURL} aria-label="Home">
          <Flex alignItems="center">
            <Image src="/images/logos/logo.svg" className="mx-auto object-fill" width="50" height="50" alt="logo" />
            <Text fontFamily="inter" fontSize="2xl" fontWeight="bold" ml="3">
              Open Assistant
            </Text>
          </Flex>
        </Link>

        <Flex alignItems="center" gap="4">
          <Flags authorizedFlags={["flagTest"]}>
            <Text>FlagTest</Text>
          </Flags>
          <AccountButton />
          <UserMenu />
        </Flex>
      </Box>
      <Divider />
    </nav>
  );
}
