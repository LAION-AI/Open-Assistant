import { BarChart2, ExternalLink, Layout, MessageCircle, MessageSquare, TrendingUp } from "lucide-react";
import { useMemo } from "react";
import { useBrowserConfig } from "src/hooks/env/BrowserEnv";

export const useSidebarItems = () => {
  const { ENABLE_CHAT } = useBrowserConfig();

  const items = useMemo(
    () => [
      ...(ENABLE_CHAT
        ? [
            {
              labelID: "chat",
              pathname: "/chat",
              icon: MessageCircle,
            },
          ]
        : []),
      {
        labelID: "dashboard",
        pathname: "/dashboard",
        icon: Layout,
      },
      {
        labelID: "messages",
        pathname: "/messages",
        icon: MessageSquare,
      },
      {
        labelID: "leaderboard",
        pathname: "/leaderboard",
        icon: BarChart2,
      },
      {
        labelID: "stats",
        pathname: "/stats",
        icon: TrendingUp,
      },
      {
        labelID: "guidelines",
        pathname: "https://projects.laion.ai/Open-Assistant/docs/guides/guidelines",
        icon: ExternalLink,
        target: "_blank",
      },
    ],
    [ENABLE_CHAT]
  );
  return items;
};
