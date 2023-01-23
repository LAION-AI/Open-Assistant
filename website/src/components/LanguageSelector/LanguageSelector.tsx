import { Select } from "@chakra-ui/react";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { useCallback, useMemo } from "react";
import cookie from "react-cookies";

const LanguageSelector = () => {
  const router = useRouter();
  const { i18n } = useTranslation();

  // Memo the set of locales and their display names.
  const localesAndNames = useMemo(() => {
    return router.locales.map((locale) => ({
      locale,
      name: new Intl.DisplayNames([locale], { type: "language" }).of(locale),
    }));
  }, [router.locales]);

  const languageChanged = useCallback(
    async (option) => {
      const locale = option.target.value;
      cookie.save("NEXT_LOCALE", locale, { path: "/" });
      const path = router.asPath;
      return router.push(path, path, { locale });
    },
    [router]
  );

  const { language: currentLanguage } = i18n;
  return (
    <Select onChange={languageChanged} defaultValue={currentLanguage}>
      {localesAndNames.map(({ locale, name }) => (
        <option key={locale} value={locale}>
          {name}
        </option>
      ))}
    </Select>
  );
};

export { LanguageSelector };
