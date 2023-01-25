import { Turnstile } from "@marsidev/react-turnstile";
import { forwardRef } from "react";

export const CloudFareCatpcha = forwardRef((ref, props) => {
  return <Turnstile siteKey={process.env.NEXT_PUBLIC_CLOUDFARE_CAPTCHA_SITE_KEY} />;
});

CloudFareCatpcha.displayName = "CloudFareCatpcha";
