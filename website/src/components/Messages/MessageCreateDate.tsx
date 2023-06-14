import { Text, useColorModeValue } from "@chakra-ui/react";
import { useCurrentLocale } from "src/hooks/locale/useCurrentLocale";

export const MessageCreateDate = ({ date }: { date: string }) => {
  const locale = useCurrentLocale();
  const createdDateColor = useColorModeValue("blackAlpha.600", "gray.400");

  return (
    <Text as="span" fontSize="small" color={createdDateColor} fontWeight="medium" me={{ base: 3, md: 6 }}>
      {new Intl.DateTimeFormat(locale, {
        hour: "2-digit",
        minute: "2-digit",
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      }).format(new Date(date))}
    </Text>
  );
};
