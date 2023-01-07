import { Box, useColorMode } from "@chakra-ui/react";
import { MenuButtonOption, SideMenu } from "src/components/SideMenu";
import { colors } from "styles/Theme/colors";

interface SideMenuLayoutProps {
  menuButtonOptions: MenuButtonOption[];
  children: React.ReactNode;
}

export const SideMenuLayout = (props: SideMenuLayoutProps) => {
  const { colorMode } = useColorMode();

  return (
    <Box backgroundColor={colorMode === "light" ? colors.light.bg : colors.dark.bg} className="sm:overflow-hidden">
      <Box className="sm:flex h-full gap-6">
        <Box className="p-6 sm:pr-0">
          <SideMenu buttonOptions={props.menuButtonOptions} />
        </Box>
        <Box className="flex flex-col overflow-auto p-6 sm:pl-0 gap-14">{props.children}</Box>
      </Box>
    </Box>
  );
};
