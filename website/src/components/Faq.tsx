import { Box, List, ListItem, Text, useColorMode } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";

import { Container } from "./Container";

const FAQS = Array.from({ length: 6 });

export function Faq() {
  const { colorMode } = useColorMode();
  const { t } = useTranslation("index");
  const headingColorClass = colorMode === "light" ? "text-gray-900" : "text-white";
  const textColorClass = colorMode === "light" ? "text-gray-700" : "text-gray-100";

  return (
    <Box as="section" id="faq" aria-labelledby="faqs-title" className="border-t border-gray-200 py-20 sm:py-32">
      <Container className="">
        <Box className="mx-auto max-w-2xl lg:mx-0">
          <Text as="h2" id="faqs-title" className={`text-3xl font-medium tracking-tight ${headingColorClass}`}>
            {t("faq_title")}
          </Text>
        </Box>
        <List
          role="list"
          className="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-16 sm:mt-20 lg:max-w-none lg:grid-cols-3"
        >
          {FAQS.map((_, index) => {
            return (
              <ListItem className="space-y-10" key={`question_${index}`}>
                <Text as="h3" className={`text-lg font-semibold leading-6 ${headingColorClass}`}>
                  {t(`faq_items.q${index as 0}`)}
                </Text>
                <Text as="p" className={`mt-4 text-sm ${textColorClass}`}>
                  {t(`faq_items.a${index as 0}`)}
                </Text>
              </ListItem>
            );
          })}
        </List>
      </Container>
    </Box>
  );
}
