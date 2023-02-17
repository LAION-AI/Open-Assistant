import { Select } from "@chakra-ui/react";
import { useRouter } from "next/router";
import { useCallback, useEffect, useMemo, useRef } from "react";
import { Cookies } from "react-cookie";
import { getLocaleDisplayName } from "src/lib/languages";

const LanguageSelector = () => {
  const localeBroadcastRef = useRef(new BroadcastChannel("locale"));
  const localeBroadcast = localeBroadcastRef.current;
  const router = useRouter();

  // the cookie is the source of truth for the locale, and it always overrides the locale of the router
  // however, if you want to render stuff dynamically you can use `router.locale` (which is not possible
  // with the cookie)

  const setLocale = useCallback(
    async (locale: string) => {
      // always update the router / paths
      // especially relevant when the event comes from another tab
      const path = router.asPath;
      await router.push(path, path, { locale });

      // we don't use cookie hooks because they don't sync in realtime when events come from other tabs
      const cookies = new Cookies();
      const currentLocale = cookies.get("NEXT_LOCALE");
      if (locale !== currentLocale) {
        // update the cookie
        cookies.set("NEXT_LOCALE", locale, { path: "/" });
        // broadcast to other tabs
        localeBroadcast.postMessage(locale);
      }
    },
    [localeBroadcast, router]
  );

  // listen for locale messages between browser tabs
  useEffect(() => {
    const languageChangeHandler = (event: MessageEvent) => setLocale(event.data);
    localeBroadcast.addEventListener("message", languageChangeHandler);
    return () => localeBroadcast.removeEventListener("message", languageChangeHandler);
  }, [localeBroadcast, router, setLocale]);

  const languageChanged = useCallback((option) => setLocale(option.target.value), [setLocale]);

  // Memo the set of locales and their display names.
  const localesAndNames = useMemo(
    () => router.locales.map((locale) => ({ locale, name: getLocaleDisplayName(locale) })),
    [router.locales]
  );

  return (
    <Select onChange={languageChanged} value={router.locale}>
      {localesAndNames.map(({ locale, name }) => (
        <option key={locale} value={locale}>
          {name}
        </option>
      ))}
    </Select>
  );
};

export { LanguageSelector };
