import { useCallback, useEffect, useState } from "react";

export interface RankingDisplayPreferences {
  displayMode: "vertical" | "horizontal";
  removeContentLimit: boolean;
  messagesPerRow: number;
}

const RANKING_PREFERENCES_KEY = "RANKING_DISPLAY_PREFERENCES";

const defaultPreferences: RankingDisplayPreferences = {
  displayMode: "vertical",
  removeContentLimit: false,
  messagesPerRow: 3, // Default to 3 messages per row for horizontal mode
};

export const useRankingDisplayPreferences = () => {
  const [preferences, setPreferences] = useState<RankingDisplayPreferences>(defaultPreferences);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load preferences from localStorage on mount
  useEffect(() => {
    if (typeof localStorage !== "undefined") {
      const stored = localStorage.getItem(RANKING_PREFERENCES_KEY);
      if (stored) {
        try {
          const parsed = JSON.parse(stored) as RankingDisplayPreferences;
          setPreferences({ ...defaultPreferences, ...parsed });
        } catch (error) {
          console.warn("Failed to parse ranking preferences from localStorage:", error);
        }
      }
    }
    setIsLoaded(true);
  }, []);

  // Save preferences to localStorage whenever they change
  useEffect(() => {
    if (isLoaded && typeof localStorage !== "undefined") {
      localStorage.setItem(RANKING_PREFERENCES_KEY, JSON.stringify(preferences));
    }
  }, [preferences, isLoaded]);

  const updatePreferences = useCallback((updates: Partial<RankingDisplayPreferences>) => {
    setPreferences((prev) => ({ ...prev, ...updates }));
  }, []);

  const setDisplayMode = useCallback((displayMode: "vertical" | "horizontal") => {
    updatePreferences({ displayMode });
  }, [updatePreferences]);

  const setRemoveContentLimit = useCallback((removeContentLimit: boolean) => {
    updatePreferences({ removeContentLimit });
  }, [updatePreferences]);

  const setMessagesPerRow = useCallback((messagesPerRow: number) => {
    updatePreferences({ messagesPerRow });
  }, [updatePreferences]);

  return {
    preferences,
    isLoaded,
    updatePreferences,
    setDisplayMode,
    setRemoveContentLimit,
    setMessagesPerRow,
  };
};
