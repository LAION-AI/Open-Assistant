import { useColorMode } from "@chakra-ui/react";
import { Turnstile, TurnstileInstance, TurnstileProps } from "@marsidev/react-turnstile";
import { forwardRef } from "react";
import { useBrowserConfig } from "src/hooks/env/BrowserEnv";
import { StrictOmit } from "ts-essentials";

export const CloudFlareCaptcha = forwardRef<TurnstileInstance, StrictOmit<TurnstileProps, "siteKey">>((props, ref) => {
  const { ...restProps } = props;
  const { colorMode } = useColorMode();
  const { CLOUDFLARE_CAPTCHA_SITE_KEY } = useBrowserConfig();

  if (!CLOUDFLARE_CAPTCHA_SITE_KEY) {
    return null;
  }

  return (
    <Turnstile
      ref={ref}
      {...restProps}
      siteKey={CLOUDFLARE_CAPTCHA_SITE_KEY}
      options={{
        theme: colorMode,
        ...props.options,
      }}
    />
  );
});

CloudFlareCaptcha.displayName = "CloudFlareCaptcha";
