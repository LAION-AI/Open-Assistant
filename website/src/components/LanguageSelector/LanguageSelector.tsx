import { Select } from "@chakra-ui/react";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { useCallback, useMemo } from "react";
import cookie from "react-cookies";

const LanguageSelector = () => {
  const router = useRouter();
  const { i18n } = useTranslation();

  const { language: currentLanguage } = i18n;
  const languageNames = useMemo(() => {
    return new Intl.DisplayNames([currentLanguage], {
      type: "language",
    });
  }, [currentLanguage]);

  const languageChanged = useCallback(
    async (option) => {
      const locale = option.target.value;
      cookie.save("NEXT_LOCALE", locale, { path: "/" });
      const path = router.asPath;
      return router.push(path, path, { locale });
    },
    [router]
  );

  const locales = router.locales;
  return (
    <Select onChange={languageChanged} defaultValue={currentLanguage}>
      {locales.map((locale) => (
        <option key={locale} value={locale}>
          {languageNames.of(locale) ?? locale}
        </option>
      ))}
    </Select>
  );
};

export { LanguageSelector };
