import path from "node:path";
import fs from "node:fs";
import chalk from "chalk";
import { fileURLToPath } from "url";
import { REST, Routes } from "discord.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
// Create a new client instance
const rest = new REST({ version: "10" }).setToken(process.env.TOKEN);
export default async function commandHandler(client) {
  const commands = [];
  const commandsPath = path.join(__dirname, "../commands");

  const commandFiles = fs
    .readdirSync(commandsPath)
    .filter((file) => file.endsWith(".js"));

  for (const file of commandFiles) {
    const filePath = `../commands/${file}`;
    const { default: command } = await import(filePath);
    // Set a new item in the Collection with the key as the command name and the value as the exported module
    if ("data" in command && "execute" in command) {
      client.commands.set(command.data.name, command);
      commands.push(command.data.toJSON());
    } else {
      console.log(
        chalk.yellow(
          `[WARNING] The command at ${filePath} is missing a required "data" or "execute" property.`
        )
      );
    }
  }

  // Construct and prepare an instance of the REST module
  // and deploy your commands!

  (async () => {
    try {
      console.log(
        `Started refreshing ${commands.length} application (/) commands.`
      );
      // The put method is used to fully refresh all commands in the guild with the current set
      const data = await rest.put(
        Routes.applicationCommands(process.env.CLIENT_ID),
        { body: commands }
      );

      console.log(`Successfully reloaded application (/) commands.`);
    } catch (error) {
      // And of course, make sure you catch and log any errors!
      console.log(error);
    }
  })();
}
