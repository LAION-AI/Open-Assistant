export async function getTranlation(lang: string) {
  var res = await fetch(
    `https://open-assistant.io/locales/${lang}/common.json`
  );
  var json = await res.json();
  var res2 = await fetch(
    `https://open-assistant.io/locales/${lang}/tasks.json`
  );
  var json2 = await res2.json();
  var res3 = await fetch(
    `https://open-assistant.io/locales/${lang}/dashboard.json`
  );
  var json3 = await res3.json();
  var res4 = await fetch(
    `https://open-assistant.io/locales/${lang}/leaderboard.json`
  );
  var json4 = await res4.json();
  var res5 = await fetch(
    `https://open-assistant.io/locales/${lang}/labelling.json`
  );
  var json5 = await res5.json();
  var res6 = await fetch(
    `https://open-assistant.io/locales/${lang}/message.json`
  );
  var json6 = await res6.json();
  var res7 = await fetch(
    `https://open-assistant.io/locales/${lang}/index.json`
  );
  var json7 = await res7.json();
  var translationObject = {
    ...json,
    ...json2,
    ...json3,
    ...json4,
    ...json5,
    ...json6,
    ...json7,
  };
  if (!translationObject["skip"]) {
    var englishTranslation = await getTranlation("en");
    translationObject["skip"] = englishTranslation["skip"];
  }
  return translationObject;
}

var locales = [
  "en",
  "ar",
  "bn",
  "ca",
  "da",
  "de",
  "es",
  "eu",
  "fa",
  "fr",
  "gl",
  "hu",
  "it",
  "ja",
  "ko",
  "pl",
  "pt-BR",
  "ru",
  "uk-UA",
  "vi",
  "zh",
  "th",
  "tr",
  "id",
];
export { locales };

const missingDisplayNamesForLocales = {
  eu: "Euskara",
  gl: "Galego",
};

/**
 * Returns the locale's name.
 */
export const getLocaleDisplayName = (
  locale: string,
  displayLocale = undefined
) => {
  // Intl defaults to English for locales that are not officially translated
  if (missingDisplayNamesForLocales[locale]) {
    return missingDisplayNamesForLocales[locale];
  }
  const displayName = new Intl.DisplayNames([displayLocale || locale], {
    type: "language",
  }).of(locale);
  // Return the Titlecased version of the language name.
  return displayName.charAt(0).toLocaleUpperCase() + displayName.slice(1);
};
