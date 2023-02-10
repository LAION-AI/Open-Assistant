/**
 * Returns the locale's name.
 */
export const getLocaleDisplayName = (locale, displayLocale = undefined) => {
  // Different browsers seem to handle "eu" differently from the Node server.
  // Special case this to avoid a hydration failure.
  if (locale === "eu") {
    return "Eurakasa";
  }
  const displayName = new Intl.DisplayNames([displayLocale || locale], { type: "language" }).of(locale);
  // Return the Titlecased version of the language name.
  return displayName.charAt(0).toLocaleUpperCase() + displayName.slice(1);
};
