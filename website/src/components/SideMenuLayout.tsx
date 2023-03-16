import { Box, useColorMode } from "@chakra-ui/react";
import { MenuButtonOption, SideMenu } from "src/components/SideMenu";
import { colors } from "src/styles/Theme/colors";

interface SideMenuLayoutProps {
  menuButtonOptions: MenuButtonOption[];
  children: React.ReactNode;
}

export const SideMenuLayout = (props: SideMenuLayoutProps) => {
  const { colorMode } = useColorMode();

  return (
    <Box backgroundColor={colorMode === "light" ? "gray.100" : colors.dark.bg} className="sm:overflow-hidden">
      <Box display="flex" flexDirection={["column", "row"]} h="full" gap={["0", "0", "0", "6"]}>
        <Box p={["3", "3", "3", "6"]} pe={["3", "3", "3", "0"]}>
          <SideMenu buttonOptions={props.menuButtonOptions} />
        </Box>
        <Box
          className="p-3 lg:p-6 ltr:lg:pl-0 rtl:lg:pr-0 w-full"
          overflowX="hidden"
          overflowY={{ base: "hidden", sm: "auto" }}
        >
          {props.children}
        </Box>
      </Box>
    </Box>
  );
};
