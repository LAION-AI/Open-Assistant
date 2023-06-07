import { HStack } from "@chakra-ui/react";
import { Icon } from "@chakra-ui/react";
import { Star } from "lucide-react";
import { useSession } from "next-auth/react";
import { useTranslation } from "next-i18next";
import { useUserScore } from "src/hooks/ui/useUserScore";

export const UserScore = () => {
  const { status } = useSession();
  const { score } = useUserScore();
  const { t } = useTranslation("leaderboard");

  if (status !== "authenticated" || !Number.isFinite(score)) {
    return null;
  }

  return (
    <HStack gap="1" title={t("score")}>
      <>{score}</>
      <Icon as={Star} fill="gold" w="5" h="5" color="gold" />
    </HStack>
  );
};
