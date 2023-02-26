import path from "node:path";
import fs from "node:fs";
import chalk from "chalk";
import { fileURLToPath } from "url";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default async function interactionsHandler(client) {
  const interactionsPath = path.join(__dirname, "../interactions");
  const interactionFiles = fs
    .readdirSync(interactionsPath)
    .filter((file) => file.endsWith(".js"));
  const interactions = [];
  if (!client.interactions)
    return console.log(
      chalk.yellow(`[WARNING] Missing interactions collection.`)
    );

  for (const file of interactionFiles) {
    const filePath = `../interactions/${file}`;
    const { default: interaction } = await import(filePath);
    // Set a new item in the Collection with the key as the command name and the value as the exported module
    if ("data" in interaction && "execute" in interaction) {
      client.interactions.set(interaction.data.customId, interaction);
      interactions.push(interaction.data);
    } else {
      console.log(
        chalk.yellow(
          `[WARNING] The interaction at ${filePath} is missing a required "data" or "execute" property.`
        )
      );
    }
  }
}
