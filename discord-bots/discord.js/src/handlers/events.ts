import path from "node:path";
import fs from "node:fs";
import { Client } from "discord.js";
import { fileURLToPath } from "url";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default async function eventHandler(client: Client) {
  const eventsPath = path.join(__dirname, "../events");
  const eventFiles = fs
    .readdirSync(eventsPath)
    .filter((file) => file.endsWith(".js"));

  for (const file of eventFiles) {
    const filePath = `../events/${file}`;
    const { default: event } = await import(filePath);
    if (event.once) {
      client.once(event.name, async (...args) =>
        event.execute(...args, client)
      );
    } else {
      client.on(event.name, async (...args) => {
        await event.execute(...args, client);
      });
    }
  }
}
