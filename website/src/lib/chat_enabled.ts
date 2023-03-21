export const isChatEnabled = () => {
  return process.env.NODE_ENV === "development" || process.env.ENABLE_CHAT === "true";
};
