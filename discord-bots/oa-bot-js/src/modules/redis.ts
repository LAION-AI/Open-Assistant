import { createClient, defineScript } from "redis";

const redisClient = createClient({
  password: process.env.REDIS_PASSWORD,
});

redisClient.on("error", (err) => console.log("Client error: Redis", err));

await redisClient.connect();

export default redisClient;
