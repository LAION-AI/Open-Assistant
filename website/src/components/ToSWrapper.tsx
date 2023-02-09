import { Box, Flex, Text } from "@chakra-ui/react";
import { useSession } from "next-auth/react";
import { useTranslation } from "next-i18next";
import { ReactNode, useMemo } from "react";
import { SubmitButton } from "src/components/Buttons/Submit";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { TermsOfService } from "src/components/ToS";
import { post } from "src/lib/api";

const navigateAway = () => {
  location.href = "https://laion.ai/";
};

const acceptToS = async () => {
  await post("/api/tos", { arg: {} });
  location.reload();
};

export const ToSWrapper = ({ children }: { children?: ReactNode | undefined }) => {
  const { t } = useTranslation("tos");
  const { data: session, status } = useSession();
  const hasAcceptedTos = Boolean(session?.user.tosAcceptanceDate);
  const isLoading = status === "loading";
  const notLoggedIn = status === "unauthenticated";

  const contents = useMemo(
    () => (
      <Box className="oa-basic-theme">
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
            <SubmitButton onClick={acceptToS} colorScheme="blue" data-cy="accept-tos">
              {t("accept")}
            </SubmitButton>
          </Flex>
        </SurveyCard>
      </Box>
    ),
    [t]
  );

  if (notLoggedIn || isLoading || hasAcceptedTos) {
    return <>{children}</>;
  }
  return contents;
};
