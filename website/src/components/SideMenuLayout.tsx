import { Box, BoxProps } from "@chakra-ui/react";
import { PropsWithChildren } from "react";
import { SIDE_MENU_WIDTH, SideMenu, SideMenuProps } from "src/components/SideMenu";

export const SideMenuLayout = ({
  items,
  children,
  collapsed,
  innerBoxProps,
}: PropsWithChildren<SideMenuProps> & {
  innerBoxProps?: BoxProps;
}) => {
  const desktopBreakpoint = collapsed ? "lg" : "md";

  return (
    <Box
      display="flex"
      flexDirection={{ base: "column", [desktopBreakpoint]: "row" }}
      h="full"
      px={{ base: 3, lg: 6 }}
      py="6"
      position="relative"
    >
      <SideMenu items={items} collapsed={collapsed} />
      <Box
        className="innerBox"
        display="block"
        w="full"
        ms={{ md: 4, lg: 6 }}
        ps={{
          [desktopBreakpoint]: SIDE_MENU_WIDTH.MD,
          lg: collapsed ? SIDE_MENU_WIDTH.MD : SIDE_MENU_WIDTH.LG,
        }}
        mt={{ base: 6, [desktopBreakpoint]: 0 }}
        {...innerBoxProps}
      >
        {children}
      </Box>
    </Box>
  );
};
