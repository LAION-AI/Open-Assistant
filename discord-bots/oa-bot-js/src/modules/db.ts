// create a db system with JSON file, create function for adding data, updating data, deleting data, and getting data
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "url";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const dbPath = path.join(__dirname, "../../db.json");
export default class Database {
  constructor() {
    if (!fs.existsSync(dbPath)) {
      fs.writeFileSync(dbPath, `{"users": {}, "tasks": {}}`);
    }
  }
  get(table, key) {
    const data = JSON.parse(fs.readFileSync(dbPath, "utf-8"));
    return data[table][key];
  }
  set(table, key, value) {
    const data = JSON.parse(fs.readFileSync(dbPath, "utf-8"));
    data[table][key] = value;
    fs.writeFileSync(dbPath, JSON.stringify(data));
  }
  delete(key) {
    const data = JSON.parse(fs.readFileSync(dbPath, "utf-8"));
    delete data[key];
    fs.writeFileSync(dbPath, JSON.stringify(data));
  }
}
