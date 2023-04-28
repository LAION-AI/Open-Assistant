import { Box, Button, Card, Text, Tooltip } from "@chakra-ui/react";
import clsx from "clsx";
import { LucideIcon } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { getTypeSafei18nKey } from "src/lib/i18n";

import { HEADER_HEIGHT } from "./Header/Header";

export interface SideMenuItemType {
  labelID: string;
  pathname: string;
  icon: LucideIcon;
  target?: HTMLAnchorElement["target"];
}

export interface SideMenuProps {
  items: SideMenuItemType[];
}

export const SIDE_MENU_WIDTH = {
  MD: `100px`,
  LG: `280px`,
};

export function SideMenu({ items }: SideMenuProps) {
  return (
    <Card
      position={{ base: "relative", md: "fixed" }}
      p={{ base: 4, md: 3, lg: 4 }}
      width={{
        base: "100%",
        md: SIDE_MENU_WIDTH.MD,
        lg: SIDE_MENU_WIDTH.LG,
      }}
      height={{ base: "auto", md: `calc(100vh - ${HEADER_HEIGHT} - ${1.5 * 2}rem)` }}
    >
      <Box
        as="nav"
        gap="2"
        display={{ base: "grid", md: "flex" }}
        flexDirection="column"
        className="grid-cols-3 col-span-3"
      >
        {items.map((item) => (
          <SideMenuItem item={item} key={item.labelID} variant="default"></SideMenuItem>
        ))}
      </Box>
    </Card>
  );
}

export const SideMenuItem = ({
  item,
  variant = "default",
  active,
}: {
  item: SideMenuItemType;
  variant: "default" | "chat";
  active?: boolean;
}) => {
  const isChat = variant === "chat";
  const router = useRouter();
  const { t } = useTranslation();
  const label = t(getTypeSafei18nKey(item.labelID));
  const isActive = active ?? router.pathname === item.pathname;
  return (
    <Tooltip
      key={item.labelID}
      label={label}
      placement="right"
      className={clsx("hidden sm:block", { "lg:hidden": !isChat })}
    >
      <Button
        as={Link}
        key={item.labelID}
        href={item.pathname}
        target={item.target}
        className="no-underline"
        gap={3}
        borderRadius={isChat ? "2xl" : "lg"}
        size="lg"
        justifyContent={{ base: "center", lg: isChat ? "center" : "start" }}
        width="full"
        p={isChat ? 2 : undefined}
        bg={isActive ? "blue.500" : undefined}
        _hover={isActive ? { bg: "blue.600" } : undefined}
      >
        <item.icon size={"1em"} className={isActive ? "text-blue-200" : undefined} />
        <Text
          fontWeight="normal"
          color={isActive ? "white" : undefined}
          className={clsx("hidden", { "lg:block": !isChat })}
        >
          {label}
        </Text>
      </Button>
    </Tooltip>
  );
};
