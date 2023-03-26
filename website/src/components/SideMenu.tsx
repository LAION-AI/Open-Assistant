import { Box, Button, Card, Text, Tooltip } from "@chakra-ui/react";
import { LucideIcon } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { getTypeSafei18nKey } from "src/lib/i18n";

import { HEADER_HEIGHT } from "./Header/Header";

export interface SideMenuItem {
  labelID: string;
  pathname: string;
  icon: LucideIcon;
  target?: HTMLAnchorElement["target"];
}

export interface SideMenuProps {
  items: SideMenuItem[];
}

export const SIDE_MENU_WIDTH = {
  MD: `100px`,
  LG: `280px`,
};

export function SideMenu({ items }: SideMenuProps) {
  const router = useRouter();
  const { t } = useTranslation();

  return (
    <Card
      position={{ base: "relative", md: "fixed" }}
      p="4"
      width={{ base: "100%", md: SIDE_MENU_WIDTH.MD, lg: SIDE_MENU_WIDTH.LG }}
      height={{ base: "auto", md: `calc(100vh - ${HEADER_HEIGHT} - ${1.5 * 2}rem)` }}
    >
      <Box
        as="nav"
        gap="2"
        display={{ base: "grid", md: "flex" }}
        flexDirection="column"
        className="grid-cols-3 col-span-3"
      >
        {items.map((item) => {
          const label = t(getTypeSafei18nKey(item.labelID));
          return (
            <Tooltip
              key={item.labelID}
              fontFamily="inter"
              label={label}
              placement="right"
              className="hidden lg:hidden sm:block"
            >
              <Link
                key={item.labelID}
                href={item.pathname}
                target={!item.target ? "_self" : item.target}
                className="no-underline"
              >
                <Button
                  justifyContent={["center", "center", "center", "start"]}
                  gap="3"
                  size="lg"
                  width="full"
                  bg={router.pathname === item.pathname ? "blue.500" : undefined}
                  _hover={router.pathname === item.pathname ? { bg: "blue.600" } : undefined}
                >
                  <item.icon size={"1em"} className={router.pathname === item.pathname ? "text-blue-200" : undefined} />
                  <Text
                    fontWeight="normal"
                    color={router.pathname === item.pathname ? "white" : undefined}
                    className="hidden lg:block"
                  >
                    {label}
                  </Text>
                </Button>
              </Link>
            </Tooltip>
          );
        })}
      </Box>
    </Card>
  );
}
