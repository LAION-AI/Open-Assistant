import axios from "axios";
import { withoutRole } from "src/lib/auth";
import { createInferenceAccessors } from "src/lib/oasst_inference_auth";
import { InferenceTokens } from "src/types/Chat";

export default withoutRole("banned", async (req, res, token) => {
  const { code, parts } = req.query;

  if (!Array.isArray(parts) || parts.length !== 1) {
    return res.status(400).end();
  }

  const { auth } = createInferenceAccessors(req, res);
  const [provider] = parts as string[];
  const url = process.env.INFERENCE_SERVER_HOST + `/auth/callback/${provider}?code=${code}`;
  const { data } = await axios<InferenceTokens>(url);
  auth.tokens = data;
  // TODO: redirect to original page the user was on, use the state query parameter
  return res.redirect(`/chat`);
});
