import { Alert, useColorMode } from "@chakra-ui/react";
import { Turnstile, TurnstileInstance, TurnstileProps } from "@marsidev/react-turnstile";
import { forwardRef } from "react";

export const CloudFlareCaptcha = forwardRef<TurnstileInstance, Omit<TurnstileProps, "siteKey">>((props, ref) => {
  const { colorMode } = useColorMode();
  const siteKey = process.env.NEXT_PUBLIC_ENABLE_EMAIL_SIGNIN_CAPTCHA;

  if (!siteKey) {
    return <Alert>Captcha site key is missisng</Alert>;
  }

  return (
    <Turnstile
      ref={ref}
      {...props}
      siteKey={siteKey}
      options={{
        theme: colorMode,
        ...props.options,
      }}
    />
  );
});

CloudFlareCaptcha.displayName = "CloudFlareCaptcha";
