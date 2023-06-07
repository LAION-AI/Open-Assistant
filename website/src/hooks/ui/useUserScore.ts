import { useSession } from "next-auth/react";
import { get } from "src/lib/api";
import { LeaderboardEntity, LeaderboardTimeFrame } from "src/types/Leaderboard";
import uswSWRImmutable from "swr/immutable";

// https://github.com/LAION-AI/Open-Assistant/issues/1957
function* generateThresholds(baseline = 3, alpha = 1.1521, maxLevel = 100) {
  let sum = 0;
  yield sum;
  for (let i = 1; i < maxLevel; i++) {
    sum += i * alpha + baseline;
    yield Math.round(sum);
  }
}

const thresholds = Array.from(generateThresholds());

export const useUserScore = () => {
  const { status } = useSession();
  const isLoggedIn = status === "authenticated";
  const { data: entries } = uswSWRImmutable<Partial<{ [time in LeaderboardTimeFrame]: LeaderboardEntity }>>(
    isLoggedIn && "/api/user_stats",
    get,
    {
      dedupingInterval: 1000 * 60, // once per minute
      keepPreviousData: true,
    }
  );
  const score = entries?.total?.leader_score ?? 0;
  const level = entries?.total?.level ?? 0;

  const currentLevelScore = thresholds[level];
  const nextLevelScore = thresholds[level + 1] ?? Infinity;
  const scoreUntilNextLevel = nextLevelScore - score;
  const reachedMaxLevel = level === 100;

  return { score, level, currentLevelScore, nextLevelScore, scoreUntilNextLevel, reachedMaxLevel };
};
