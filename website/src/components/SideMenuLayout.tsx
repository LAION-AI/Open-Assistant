import { Box } from "@chakra-ui/react";
import { PropsWithChildren } from "react";
import { SIDE_MENU_WIDTH, SideMenu, SideMenuProps } from "src/components/SideMenu";

export const SideMenuLayout = ({ items, children, collapsed }: PropsWithChildren<SideMenuProps>) => {
  return (
    <Box
      display="flex"
      flexDirection={{ base: "column", md: "row" }}
      h="full"
      px={{ base: 3, lg: 6 }}
      py="6"
      position="relative"
    >
      <SideMenu items={items} collapsed={collapsed} />
      <Box
        display="block"
        w="full"
        ms={{ md: 4, lg: 6 }}
        ps={{
          md: SIDE_MENU_WIDTH.MD,
          lg: collapsed ? SIDE_MENU_WIDTH.MD : SIDE_MENU_WIDTH.LG,
        }}
        mt={{ base: 6, md: 0 }}
      >
        {children}
      </Box>
    </Box>
  );
};
