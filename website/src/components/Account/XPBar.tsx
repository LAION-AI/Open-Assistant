import { Grid, GridItem, Icon, keyframes, Progress, Text, usePrefersReducedMotion } from "@chakra-ui/react";
import { Star } from "lucide-react";
import { useTranslation } from "next-i18next";
import { useMemo } from "react";
import { useUserScore } from "src/hooks/ui/useUserScore";

const spin = keyframes`
0% {transform: rotate(0deg);}
100% {transform: rotate(360deg);}
`;
const starAnimation = `${spin} infinite 4s cubic-bezier(0.52, -0.43, 0, 1.04)`;

export const XPBar = () => {
  const { t } = useTranslation("leaderboard");
  const { level, score, scoreUntilNextLevel, reachedMaxLevel } = useUserScore();
  const useMotion = !usePrefersReducedMotion();

  const nextLevelText = useMemo(() => {
    if (reachedMaxLevel) {
      return t("reached_max_level");
    }
    return t("xp_progress_message", { need: scoreUntilNextLevel });
  }, [reachedMaxLevel, scoreUntilNextLevel, t]);

  return (
    <Grid
      rowGap={1}
      columnGap={6}
      templateAreas={`
       "star row1"
       "star row2"
       "star progress"
    `}
      gridTemplateColumns="auto 1fr"
      alignItems="center"
    >
      <GridItem area="star" justifySelf="center">
        <Icon as={Star} boxSize={20} fill="gold" color="gold" animation={useMotion && starAnimation} />
      </GridItem>
      <GridItem area="row1">
        <Text>{t("level_progress_message", { score, level })}</Text>
      </GridItem>
      <GridItem area="row2">
        <Text>{nextLevelText}</Text>
      </GridItem>
      <GridItem area="progress">
        <Progress hasStripe colorScheme="yellow" value={level} />
      </GridItem>
    </Grid>
  );
};
