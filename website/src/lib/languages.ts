import { NextApiRequest } from "next";

import { OasstError } from "./oasst_api_client";

const missingDisplayNamesForLocales = {
  eu: "Euskara",
  gl: "Galego",
};

/**
 * Returns the locale's name.
 */
export const getLocaleDisplayName = (locale: string, displayLocale?: string) => {
  // Intl defaults to English for locales that are not oficially translated
  if (missingDisplayNamesForLocales[locale]) {
    return missingDisplayNamesForLocales[locale];
  }
  const displayName = new Intl.DisplayNames([displayLocale || locale], { type: "language" }).of(locale);
  // Return the Titlecased version of the language name.
  return displayName.charAt(0).toLocaleUpperCase() + displayName.slice(1);
};

export const getLanguageFromRequest = (req: NextApiRequest) => {
  const body = req.method === "GET" ? req.query : req.body;
  const lang = body["lang"];

  if (!lang || typeof lang !== "string") {
    throw new OasstError({
      message: "Invalid language",
      httpStatusCode: -1,
      errorCode: -1,
      path: req.url!,
      method: req.method!,
    });
  }

  return lang;
};
