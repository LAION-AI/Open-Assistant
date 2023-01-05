import { Box, Button, Text, useColorMode } from "@chakra-ui/react";
import Image from "next/image";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { FaUser } from "react-icons/fa";

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
    <nav className={`oa-basic-theme ${borderClass}`}>
      <Box className="relative z-10 flex justify-between px-4 py-4">
        <div className="relative z-10 flex items-center gap-10">
          <Link href={homeURL} aria-label="Home" className="flex items-center">
            <Image src="/images/logos/logo.svg" className="mx-auto object-fill" width="50" height="50" alt="logo" />
            <Text fontFamily="inter" fontSize="2xl" fontWeight="bold" className="ml-3">
              Open Assistant
            </Text>
          </Link>
        </div>
        <div className="flex items-center gap-4">
          <AccountButton />
          <UserMenu />
        </div>
      </Box>
    </nav>
  );
}
