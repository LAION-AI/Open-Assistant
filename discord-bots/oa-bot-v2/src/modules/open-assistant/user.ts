import Database from "../db.js";

export async function getUserLang(userId: string) {
  var db = new Database();
  var lang = db.get(`open-assistant-users_${userId}_lang`);

  if (lang) {
    return lang;
  } else {
    return null;
  }
}

export async function setUserLang(userId: string, lang: string) {
  var db = new Database();
  db.set("users", userId, { lang: lang, createdAt: new Date().toISOString() });
  return true;
}
