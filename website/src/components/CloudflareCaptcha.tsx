import { useColorMode } from "@chakra-ui/react";
import { Turnstile, TurnstileInstance, TurnstileProps } from "@marsidev/react-turnstile";
import { forwardRef } from "react";

export const CloudFlareCaptcha = forwardRef<TurnstileInstance, Omit<TurnstileProps, "siteKey">>((props, ref) => {
  const { colorMode } = useColorMode();
  return (
    <Turnstile
      ref={ref}
      {...props}
      siteKey={process.env.NEXT_PUBLIC_CLOUDFLARE_CAPTCHA_SITE_KEY}
      options={{
        theme: colorMode,
        ...props.options,
      }}
    />
  );
});

CloudFlareCaptcha.displayName = "CloudFlareCaptcha";
