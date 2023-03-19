const flags = [
  { name: "flagTest", isActive: false },
  { name: "chat", isActive: process.env.NODE_ENV === "development" || process.env.ENABLE_CHAT === "true" },
];

export default flags;
