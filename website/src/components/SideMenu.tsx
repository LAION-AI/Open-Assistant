import { Box, Button, Card, Text, Tooltip } from "@chakra-ui/react";
import clsx from "clsx";
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
  collapsed?: boolean;
}

export const SIDE_MENU_WIDTH = {
  MD: `100px`,
  LG: `280px`,
};

export function SideMenu({ items, collapsed }: SideMenuProps) {
  const router = useRouter();
  const { t } = useTranslation();
  const desktopBreakpoint = collapsed ? "lg" : "md";
  return (
    <Card
      position={{ base: "relative", [desktopBreakpoint]: "fixed" }}
      p={{ base: 4, md: 3, lg: collapsed ? 3 : 4 }}
      width={{
        base: "100%",
        ...(collapsed ? { [desktopBreakpoint]: `100px` } : { md: SIDE_MENU_WIDTH.MD, lg: SIDE_MENU_WIDTH.LG }),
      }}
      height={{ base: "auto", [desktopBreakpoint]: `calc(100vh - ${HEADER_HEIGHT} - ${1.5 * 2}rem)` }}
    >
      <Box
        as="nav"
        gap="2"
        display={{ base: "grid", [desktopBreakpoint]: "flex" }}
        flexDirection="column"
        className="grid-cols-3 col-span-3"
      >
        {items.map((item) => {
          const label = t(getTypeSafei18nKey(item.labelID));
          return (
            <Tooltip
              key={item.labelID}
              label={label}
              placement="right"
              className={clsx("hidden sm:block", { "lg:hidden": !collapsed })}
            >
              <Button
                as={Link}
                key={item.labelID}
                href={item.pathname}
                target={item.target}
                className="no-underline"
                gap={3}
                borderRadius="lg"
                size="lg"
                justifyContent={{ base: "center", lg: collapsed ? "center" : "start" }}
                width="full"
                p={collapsed ? 0 : undefined}
                bg={router.pathname === item.pathname ? "blue.500" : undefined}
                _hover={router.pathname === item.pathname ? { bg: "blue.600" } : undefined}
              >
                <item.icon size={"1em"} className={router.pathname === item.pathname ? "text-blue-200" : undefined} />
                <Text
                  fontWeight="normal"
                  color={router.pathname === item.pathname ? "white" : undefined}
                  className={clsx("hidden", { "lg:block": !collapsed })}
                >
                  {label}
                </Text>
              </Button>
            </Tooltip>
          );
        })}
      </Box>
    </Card>
  );
}
