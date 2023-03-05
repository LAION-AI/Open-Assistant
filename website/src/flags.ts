const flags = [
  { name: "flagTest", isActive: false },
  { name: "chat", isActive: process.env.NODE_ENV === "development" },
];

export default flags;
