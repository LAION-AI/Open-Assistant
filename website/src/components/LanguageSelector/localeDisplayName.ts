const missingDisplayNamesForLocales = {
  gl: "Galego",
};

export const getLocaleDisplayName = (locale: string) => {
  const missingDisplayName = missingDisplayNamesForLocales[locale];

  return missingDisplayName || new Intl.DisplayNames([locale], { type: "language" }).of(locale);
};
