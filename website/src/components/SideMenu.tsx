import { Button, Card, Text, Tooltip, useColorMode } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { LucideIcon, Sun } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/router";

export interface MenuButtonOption {
  label: string;
  pathname: string;
  icon: LucideIcon;
}

export interface SideMenuProps {
  buttonOptions: MenuButtonOption[];
}

export function SideMenu(props: SideMenuProps) {
  const router = useRouter();
  const { colorMode, toggleColorMode } = useColorMode();
  const { t } = useTranslation(["side_menu", "common"]);

  return (
    <main className="sticky top-0 sm:h-full">
      <Card
        display={{ base: "grid", sm: "flex" }}
        width={["100%", "100%", "100px", "280px"]}
        className="grid-cols-3 gap-2 sm:flex-col sm:justify-between p-4 h-full"
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
                  <item.icon size={"1em"} className={router.pathname === item.pathname ? "text-blue-200" : null} />
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
      </Card>
    </main>
  );
}
