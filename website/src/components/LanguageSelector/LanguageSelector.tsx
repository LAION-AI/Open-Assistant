import { Select } from "@chakra-ui/react";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { useCallback, useEffect, useMemo } from "react";
import { useCookies } from "react-cookie";
import { getLocaleDisplayName } from "src/lib/languages";

const LanguageSelector = () => {
  const router = useRouter();
  const [cookies, setCookie] = useCookies(["NEXT_LOCALE"]);
  const { i18n } = useTranslation();

  // Inspect the cookie based locale and the router based locale.  If the user
  // has manually set the locale via URL, they will differ.  In that condition,
  // update the cookie.
  useEffect(() => {
    const localeCookie = cookies["NEXT_LOCALE"];
    const localeRouter = router.locale;
    if (localeRouter !== localeCookie) {
      setCookie("NEXT_LOCALE", localeRouter, { path: "/" });
    }
  }, [cookies, setCookie, router]);

  // Memo the set of locales and their display names.
  const localesAndNames = useMemo(() => {
    return router.locales.map((locale) => ({
      locale,
      name: getLocaleDisplayName(locale),
    }));
  }, [router.locales]);

  const languageChanged = useCallback(
    async (option) => {
      const locale = option.target.value;
      setCookie("NEXT_LOCALE", locale, { path: "/" });
      const path = router.asPath;
      await router.push(path, path, { locale });
      router.reload();
    },
    [router, setCookie]
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
