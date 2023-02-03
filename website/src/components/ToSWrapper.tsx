import { Flex, Text } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { ReactNode, useMemo } from "react";
import { SubmitButton } from "src/components/Buttons/Submit";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { useToSAcceptance } from "src/hooks/useToSAcceptance";
import { TermsOfService } from "src/pages/terms-of-service";

const navigateAway = () => {
  location.href = "https://laion.ai/";
};

export const ToSWrapper = ({ children }: { children?: ReactNode | undefined }) => {
  const { hasAcceptedTos, acceptToS } = useToSAcceptance();
  const { t } = useTranslation("tos");

  const contents = useMemo(
    () => (
      <SurveyCard display="flex" flexDir="column" w="full" maxWidth="7xl" m="auto" gap={4}>
        <Text fontWeight="bold" fontSize="xl" as="h2">
          {t("title")}
        </Text>
        <Text>{t("content")}</Text>
        <TermsOfService />
        <Flex gap={10} justifyContent="center">
          <SubmitButton onClick={navigateAway} colorScheme="red">
            {t("decline")}
          </SubmitButton>
          <SubmitButton onClick={acceptToS} colorScheme="blue">
            {t("accept")}
          </SubmitButton>
        </Flex>
      </SurveyCard>
    ),
    [acceptToS, t]
  );

  if (hasAcceptedTos) {
    return children;
  }
  return contents;
};
