import Cookies from "cookies";
import type { NextApiRequest, NextApiResponse } from "next";
import { InferenceTokens } from "src/types/Chat";

const INFERNCE_TOKEN_KEY = "inferenceToken";

export const getInferenceTokens = (req: NextApiRequest, res: NextApiResponse): InferenceTokens | null => {
  const cookies = new Cookies(req, res);
  const encoded: string | undefined = cookies.get(INFERNCE_TOKEN_KEY);
  if (encoded) {
    return JSON.parse(encoded);
  }
  return null;
};

export const setInferenceTokens = (req: NextApiRequest, res: NextApiResponse, tokens: InferenceTokens) => {
  const cookies = new Cookies(req, res);
  cookies.set(INFERNCE_TOKEN_KEY, JSON.stringify(tokens), {
    // TODO: I don't like hard coding it like this
    maxAge: 1000 * 60 * 60 * 24 * 1, // 1 day
  });
};

export const clearInferenceTokens = (req: NextApiRequest, res: NextApiResponse) => {
  const cookies = new Cookies(req, res);
  cookies.set(INFERNCE_TOKEN_KEY, null, { maxAge: 1 });
};
