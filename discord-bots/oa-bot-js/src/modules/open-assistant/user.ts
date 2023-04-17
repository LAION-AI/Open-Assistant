import axios from "axios";
import Database from "../db.js";
let db = new Database();

export async function getUserLang(userId: string) {
  let user = await db.get("users", userId);
  if (user) {
    return user.lang;
  } else {
    return null;
  }
}

export async function setUserLang(userId: string, lang: string) {
  let user = await db.get("users", userId);
  if (user && user) {
    await db.set("users", userId, {
      ...user,
      lang: lang,
    });
    return true;
  } else {
    await db.set("users", userId, {
      lang: lang,
    });
    return true;
  }
}
