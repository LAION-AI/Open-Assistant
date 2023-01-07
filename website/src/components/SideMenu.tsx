import { Box, Button, Text, Tooltip, useColorMode } from "@chakra-ui/react";
import Link from "next/link";
import { useRouter } from "next/router";
import { FiSun } from "react-icons/fi";
import { IconType } from "react-icons/lib";
import { colors } from "styles/Theme/colors";

export interface MenuButtonOption {
  label: string;
  pathname: string;
  desc: string;
  icon: IconType;
}

export interface SideMenuProps {
  buttonOptions: MenuButtonOption[];
}

export function SideMenu(props: SideMenuProps) {
  const router = useRouter();
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <main className="sticky top-0 sm:h-full">
      <Box
        width={["100%", "100%", "100px", "280px"]}
        backgroundColor={colorMode === "light" ? colors.light.div : colors.dark.div}
        boxShadow="base"
        borderRadius="xl"
        className="grid grid-cols-4 gap-2 sm:flex sm:flex-col sm:justify-between p-4 h-full"
      >
        <nav className="grid grid-cols-3 col-span-3 sm:flex sm:flex-col gap-2">
          {props.buttonOptions.map((item, itemIndex) => (
            <Tooltip
              key={itemIndex}
              fontFamily="inter"
              label={item.label}
              placement="right"
              className="hidden lg:hidden sm:block"
            >
              <Link key={`${item.label}-${itemIndex}`} href={item.pathname} style={{ textDecoration: "none" }}>
                <Button
                  justifyContent={["center", "center", "center", "left"]}
                  gap="3"
                  size="lg"
                  width="full"
                  bg={router.pathname === item.pathname ? "blue.500" : null}
                  _hover={router.pathname === item.pathname ? { bg: "blue.600" } : null}
                >
                  <item.icon className={router.pathname === item.pathname ? "text-blue-200" : null} />
                  <Text
                    fontWeight="normal"
                    color={router.pathname === item.pathname ? "white" : null}
                    className="hidden lg:block"
                  >
                    {item.label}
                  </Text>
                </Button>
              </Link>
            </Tooltip>
          ))}
        </nav>
        <div>
          <Tooltip fontFamily="inter" label="Toggle Dark Mode" placement="right" className="hidden lg:hidden sm:block">
            <Button size="lg" width="full" justifyContent="center" onClick={toggleColorMode} gap="2">
              <FiSun />
              <Text fontWeight="normal" className="hidden lg:block">
                {colorMode === "light" ? "Dark Mode" : "Light Mode"}
              </Text>
            </Button>
          </Tooltip>
        </div>
      </Box>
    </main>
  );
}
