import { useSession } from "next-auth/react";
import { get } from "src/lib/api";
import { LeaderboardEntity, LeaderboardTimeFrame } from "src/types/Leaderboard";
import uswSWRImmutable from "swr/immutable";

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
  const score: number | undefined = entries?.total?.leader_score;
  return score;
};
