import { Box } from "@chakra-ui/react";
import { PropsWithChildren } from "react";
import { SIDE_MENU_WIDTH, SideMenu, SideMenuProps } from "src/components/SideMenu";

export const SideMenuLayout = ({ items, children }: PropsWithChildren<SideMenuProps>) => {
  return (
    <Box
      display="flex"
      flexDirection={{ base: "column", md: "row" }}
      h="full"
      px={{ base: 3, lg: 6 }}
      py="6"
      position="relative"
    >
      <SideMenu items={items} />
      <Box
        display="block"
        w="full"
        ms={{ md: 6 }}
        ps={{
          md: SIDE_MENU_WIDTH.MD,
          lg: SIDE_MENU_WIDTH.LG,
        }}
        mt={{ base: 6, md: 0 }}
      >
        {children}
      </Box>
    </Box>
  );
};
