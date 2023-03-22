import Cookies from "cookies";
import type { NextApiRequest, NextApiResponse } from "next";
import { InferenceTokens } from "src/types/Chat";

import { OasstInferenceClient } from "./oasst_inference_client";

const INFERNCE_TOKEN_KEY = "inferenceToken";

export class InferenceAuth {
  private readonly cookies;
  private token?: InferenceTokens;
  constructor(req: NextApiRequest, res: NextApiResponse) {
    this.cookies = new Cookies(req, res);
    const encoded: string | undefined = this.cookies.get(INFERNCE_TOKEN_KEY);
    if (encoded) {
      this.token = JSON.parse(encoded);
    }
  }

  get tokens(): InferenceTokens | undefined {
    return this.token;
  }

  set tokens(token: InferenceTokens) {
    const encoded = JSON.stringify(token);
    this.token = token;
    this.cookies.set(INFERNCE_TOKEN_KEY, encoded, {
      maxAge: 1000 * 60 * 60 * 24 * 1, // 1 day
    });
  }
}

export const createInferenceAccessors = (req: NextApiRequest, res: NextApiResponse) => {
  const auth = new InferenceAuth(req, res);
  const token = auth.tokens?.access_token.access_token;
  const client = new OasstInferenceClient(token);
  return { auth, client };
};
