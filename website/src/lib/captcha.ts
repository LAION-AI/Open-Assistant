type CaptchaErrorCode =
  | "missing-input-secret"
  | "invalid-input-secret"
  | "missing-input-response"
  | "invalid-input-response"
  | "bad-request"
  | "timeout-or-duplicate"
  | "internal-error";

type CheckCaptchaResponse = {
  success: boolean;
  challenge_ts?: string;
  hostname?: string;
  "error-codes"?: CaptchaErrorCode[];
  action?: string;
  cdata?: string;
};

// https://developers.cloudflare.com/turnstile/get-started/server-side-validation/
export const checkCaptcha = async (
  token: string,
  ipAdress: string,
  options?: { cdata?: string; action?: string }
): Promise<CheckCaptchaResponse> => {
  if (!token) {
    return {
      success: false,
    };
  }

  const data = new URLSearchParams();

  data.append("secret", process.env.CLOUDFLARE_CAPTCHA_SECRET_KEY);
  data.append("response", token);
  data.append("remoteip", ipAdress);

  const result = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
    body: data,
    method: "POST",
  });

  const res: CheckCaptchaResponse = await result.json();
  return {
    ...res,
    success: getSuccess(res, options?.action, options?.cdata),
  };
};

// This function hasn't been tested yet, Cloudflare doesn't send `action` and `cdata` with a demo key.
const getSuccess = (response: CheckCaptchaResponse, action: string | undefined, cdata: string | undefined) => {
  if (action === undefined && cdata === undefined) {
    return response.success;
  }

  if (action) {
    if (cdata) {
      return response.action === action && response.cdata === cdata;
    }
    return response.action === action;
  }

  return false;
};
