import { Select, Stack } from "@chakra-ui/react";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { useCallback, useMemo } from "react";
import { getLocaleDisplayName } from "src/lib/languages";

const GeneralLanguageSelector = (props: {
  handleChange: (newValue?: string) => void;
  permitNoInput?: boolean;
  noInputPlaceholderValue?: string;
}) => {
  const router = useRouter();
  const { i18n } = useTranslation();
  const { language: selectedLanguage } = i18n;

  // Memo the set of locales and their display names.
  const localesAndNames = useMemo(() => {
    return router.locales!.map((locale) => ({
      locale,
      name: getLocaleDisplayName(locale),
    }));
  }, [router.locales]);

  const languageChanged = useCallback(
    async (option) => {
      const locale = option.target.value as string;
      if (props.handleChange) props.handleChange(locale === "none" ? undefined : locale);
    },
    [props]
  );

  return (
    <Stack>
      <Select onChange={languageChanged} defaultValue={props.permitNoInput ? "none" : selectedLanguage}>
        {props.permitNoInput ? (
          <option key="none" value="none">
            {props.noInputPlaceholderValue}
          </option>
        ) : undefined}
        {localesAndNames.map(({ locale, name }) => (
          <option key={locale} value={locale}>
            {name}
          </option>
        ))}
      </Select>
    </Stack>
  );
};

export { GeneralLanguageSelector };
