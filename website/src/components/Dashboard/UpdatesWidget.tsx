import { Card, CardBody, Link, Text, VStack, HStack, Badge, Skeleton } from "@chakra-ui/react";
import NextLink from "next/link";
import { useTranslation } from "next-i18next";
import { useEffect, useState } from "react";

interface NewsItem {
  id: string;
  title: string;
  date: string;
  url?: string;
  isNew?: boolean;
}

// Default news items (fallback if RSS fetch fails)
const DEFAULT_NEWS: NewsItem[] = [
  {
    id: "1",
    title: "Welcome to Open Assistant!",
    date: new Date().toISOString().split("T")[0],
    isNew: true,
  },
];

// RSS Feed URL (configurable)
const RSS_FEED_URL = process.env.NEXT_PUBLIC_OA_RSS_FEED || "";

export function UpdatesWidget() {
  const { t } = useTranslation(["dashboard"]);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        // Try to fetch from RSS feed if configured
        if (RSS_FEED_URL) {
          const response = await fetch(RSS_FEED_URL);
          if (response.ok) {
            const data = await response.text();
            // Simple RSS parsing (can be enhanced with a proper RSS parser)
            const parser = new DOMParser();
            const xml = parser.parseFromString(data, "text/xml");
            const items = xml.querySelectorAll("item");
            
            const parsedNews: NewsItem[] = Array.from(items).slice(0, 5).map((item, index) => ({
              id: String(index),
              title: item.querySelector("title")?.textContent || "",
              date: item.querySelector("pubDate")?.textContent?.split("T")[0] || "",
              url: item.querySelector("link")?.textContent || "",
              isNew: index === 0, // Mark first item as new
            }));
            
            setNews(parsedNews);
          } else {
            setNews(DEFAULT_NEWS);
          }
        } else {
          // Use default news if no RSS configured
          setNews(DEFAULT_NEWS);
        }
      } catch (error) {
        console.error("Failed to fetch news:", error);
        setNews(DEFAULT_NEWS);
      } finally {
        setIsLoading(false);
      }
    };

    fetchNews();
  }, []);

  // Check if news was read (stored in localStorage)
  const [readNews, setReadNews] = useState<Set<string>>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("oa-read-news");
      return saved ? new Set(JSON.parse(saved)) : new Set();
    }
    return new Set();
  });

  const markAsRead = (id: string) => {
    const newRead = new Set(readNews);
    newRead.add(id);
    setReadNews(newRead);
    if (typeof window !== "undefined") {
      localStorage.setItem("oa-read-news", JSON.stringify([...newRead]));
    }
  };

  return (
    <main className="h-fit col-span-3">
      <div className="flex flex-col gap-4">
        <div className="flex items-end justify-between">
          <HStack>
            <Text className="text-2xl font-bold">{t("latest_updates")}</Text>
            {news.some((n) => n.isNew && !readNews.has(n.id)) && (
              <Badge colorScheme="red" variant="solid">
                {t("new")}
              </Badge>
            )}
          </HStack>
          <Link as={NextLink} href="/updates" _hover={{ textDecoration: "none" }}>
            <Text color="blue.400" className="text-sm font-bold">
              {t("view_all")} -&gt;
            </Text>
          </Link>
        </div>
        <Card>
          <CardBody>
            <VStack align="stretch" spacing={3}>
              {isLoading ? (
                <>
                  <Skeleton height="20px" />
                  <Skeleton height="20px" />
                  <Skeleton height="20px" />
                </>
              ) : news.length === 0 ? (
                <Text color="gray.500">{t("no_updates")}</Text>
              ) : (
                news.map((item) => (
                  <HStack
                    key={item.id}
                    justify="space-between"
                    p={2}
                    borderRadius="md"
                    bg={readNews.has(item.id) ? undefined : "blue.50"}
                    _dark={{ bg: readNews.has(item.id) ? undefined : "blue.900" }}
                    cursor="pointer"
                    onClick={() => markAsRead(item.id)}
                    as={item.url ? Link : undefined}
                    href={item.url}
                    isExternal={!!item.url}
                  >
                    <HStack>
                      {item.isNew && !readNews.has(item.id) && (
                        <Badge colorScheme="red" size="sm">
                          {t("new")}
                        </Badge>
                      )}
                      <Text
                        fontWeight={readNews.has(item.id) ? "normal" : "semibold"}
                        color={readNews.has(item.id) ? "gray.600" : undefined}
                        _dark={{ color: readNews.has(item.id) ? "gray.400" : undefined }}
                      >
                        {item.title}
                      </Text>
                    </HStack>
                    <Text fontSize="sm" color="gray.500">
                      {item.date}
                    </Text>
                  </HStack>
                ))
              )}
            </VStack>
          </CardBody>
        </Card>
      </div>
    </main>
  );
}
