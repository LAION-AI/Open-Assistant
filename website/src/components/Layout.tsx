import { Box } from "@chakra-ui/react";
import { Activity, BarChart2, MessageSquare, Settings, Users } from "lucide-react";
import type { NextPage } from "next";
import { PropsWithChildren } from "react";
import { useSidebarItems } from "src/hooks/layout/sidebarItems";

import { SlimFooter } from "./Dashboard/SlimFooter";
import { Footer } from "./Footer";
import { HeaderLayout } from "./Header/Header";
import { SideMenuLayout } from "./SideMenuLayout";
import { ToSWrapper } from "./ToSWrapper";

export type NextPageWithLayout<P = unknown, IP = P> = NextPage<P, IP> & {
  getLayout?: (props: PropsWithChildren) => JSX.Element;
};

export const DefaultLayout = ({ children }: PropsWithChildren) => (
  <HeaderLayout>
    {children}
    <Footer />
  </HeaderLayout>
);

export const DashboardLayout = ({ children }: PropsWithChildren) => {
  const items = useSidebarItems();
  return (
    <HeaderLayout>
      <ToSWrapper>
        <SideMenuLayout items={items}>
          <Box>{children}</Box>
          <Box mt="10">
            <SlimFooter />
          </Box>
        </SideMenuLayout>
      </ToSWrapper>
    </HeaderLayout>
  );
};

export const AdminLayout = ({ children }: PropsWithChildren) => (
  <HeaderLayout>
    <SideMenuLayout
      items={[
        {
          labelID: "users",
          pathname: "/admin",
          icon: Users,
        },
        {
          labelID: "Messages",
          pathname: "/admin/messages",
          icon: MessageSquare,
        },
        {
          labelID: "trollboard",
          pathname: "/admin/trollboard",
          icon: BarChart2,
        },
        {
          labelID: "status",
          pathname: "/admin/status",
          icon: Activity,
        },
        {
          labelID: "parameters",
          pathname: "/admin/parameters",
          icon: Settings,
        },
      ]}
    >
      <Box>{children}</Box>
    </SideMenuLayout>
  </HeaderLayout>
);
