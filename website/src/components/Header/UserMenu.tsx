import { Avatar, Box, Link, Menu, MenuButton, MenuDivider, MenuItem, MenuList, Text } from "@chakra-ui/react";
import { signOut, useSession } from "next-auth/react";
import React from "react";
import { FiAlertTriangle, FiLayout, FiLogOut, FiSettings, FiShield } from "react-icons/fi";

export function UserMenu() {
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
          <MenuButton border="solid" borderRadius="full" borderWidth="thin" borderColor="blackAlpha.300">
            <Box display="flex" alignItems="center" gap="3" p="1" paddingRight={[1, 1, 1, 6, 6]}>
              <Avatar size="sm" bgImage={session.user.image}></Avatar>
              <p data-cy="username" className="hidden lg:flex">
                {session.user.name || session.user.email}
              </p>
            </Box>
          </MenuButton>
          <MenuList p="2" borderRadius="xl">
            <Box display="flex" flexDirection="column" alignItems="center" borderRadius="md" p="4">
              <Text>Your Score</Text>
              <Text color="blue.500" fontWeight="bold" fontSize="xl">
                3,200
              </Text>
            </Box>
            <MenuDivider></MenuDivider>
            {accountOptions.map((item) => (
              <Link key={item.name} href={item.href} _hover={{ textDecoration: "none" }}>
                <MenuItem gap="3" borderRadius="md" p="4">
                  <item.icon className="text-blue-500" aria-hidden="true" />
                  <Text>{item.name}</Text>
                </MenuItem>
              </Link>
            ))}

            <MenuDivider></MenuDivider>
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
