import {
  Avatar,
  Box,
  Link,
  Menu,
  MenuButton,
  MenuDivider,
  MenuGroup,
  MenuItem,
  MenuList,
  Text,
  useColorModeValue,
} from "@chakra-ui/react";
import { signOut, useSession } from "next-auth/react";
import NextLink from "next/link";
import React from "react";
import { FiAlertTriangle, FiLayout, FiLogOut, FiSettings, FiShield } from "react-icons/fi";

export function UserMenu() {
  const borderColor = useColorModeValue("gray.300", "gray.600");

  const { data: session } = useSession();

  if (!session) {
    return <></>;
  }
  if (session && session.user) {
    const accountOptions = [
      {
        name: "Dashboard",
        href: "/dashboard",
        desc: "Dashboard",
        icon: FiLayout,
      },
      {
        name: "Account Settings",
        href: "/account",
        desc: "Account Settings",
        icon: FiSettings,
      },
    ];
    const helpOptions = [
      {
        name: "Report a Bug",
        href: "https://github.com/LAION-AI/Open-Assistant/issues/new/choose",
        desc: "Report a Bug",
        icon: FiAlertTriangle,
      },
    ];

    if (session.user.role === "admin") {
      accountOptions.unshift({
        name: "Admin Dashboard",
        href: "/admin",
        desc: "Admin Dashboard",
        icon: FiShield,
      });
    }

    return (
      <>
        <Menu>
          <MenuButton border="solid" borderRadius="full" borderWidth="thin" borderColor={borderColor}>
            <Box display="flex" alignItems="center" gap="3" p="1" paddingRight={[1, 1, 1, 6, 6]}>
              <Avatar size="sm" bgImage={session.user.image}></Avatar>
              <Text data-cy="username" className="hidden lg:flex">
                {session.user.name || session.user.email}
              </Text>
            </Box>
          </MenuButton>
          <MenuList p="2" borderRadius="xl" shadow="none">
            <Box display="flex" flexDirection="column" alignItems="center" borderRadius="md" p="4">
              <Text>{session.user.name}</Text>
              <Text color="blue.500" fontWeight="bold" fontSize="xl">
                3,200
              </Text>
            </Box>
            <MenuDivider />
            <MenuGroup>
              {accountOptions.map((item) => (
                <Link as={NextLink} key={item.name} href={item.href} _hover={{ textDecoration: "none" }}>
                  <MenuItem gap="3" borderRadius="md" p="4">
                    <item.icon className="text-blue-500" aria-hidden="true" />
                    <Text>{item.name}</Text>
                  </MenuItem>
                </Link>
              ))}
            </MenuGroup>
            <MenuDivider />
            <MenuGroup>
              {helpOptions.map((item) => (
                <Link as={NextLink} key={item.name} href={item.href} isExternal _hover={{ textDecoration: "none" }}>
                  <MenuItem gap="3" borderRadius="md" p="4">
                    <item.icon className="text-blue-500" aria-hidden="true" />
                    <Text>{item.name}</Text>
                  </MenuItem>
                </Link>
              ))}
            </MenuGroup>
            <MenuDivider />
            <MenuItem gap="3" borderRadius="md" p="4" onClick={() => signOut({ callbackUrl: "/" })}>
              <FiLogOut className="text-blue-500" aria-hidden="true" />
              <Text>Sign Out</Text>
            </MenuItem>
          </MenuList>
        </Menu>
      </>
    );
  }
}

export default UserMenu;
