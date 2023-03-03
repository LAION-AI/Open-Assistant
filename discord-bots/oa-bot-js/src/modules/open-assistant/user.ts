import axios from "axios";
import supabase from "../supabase.js";

export async function getUserLang(userId: string) {
  var { data: user } = await supabase
    .from("open_assistant_users")
    .select("*")
    .eq("id", userId);
  if (user && user[0]) {
    return user[0].lang;
  } else {
    return null;
  }
}

export async function setUserLang(userId: string, lang: string) {
  var { data: user } = await supabase
    .from("open_assistant_users")
    .select("*")
    .eq("id", userId);
  if (user && user[0]) {
    await supabase
      .from("open_assistant_users")
      .update({ lang: lang })
      .eq("id", userId);
    return true;
  } else {
    await supabase.from("open_assistant_users").insert([
      {
        id: userId,
        lang: lang,
      },
    ]);
    return true;
  }
}
