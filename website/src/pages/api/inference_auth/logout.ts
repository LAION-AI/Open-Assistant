import { withoutRole } from "src/lib/auth";
import { clearInferenceTokens } from "src/lib/oasst_inference_auth";

export default withoutRole("banned", async (req, res, token) => {
  clearInferenceTokens(req, res);
  // note: maybe we want to communicate something to the inference backend?
  // like revoking tokens and such?
  return res.redirect(`/chat`);
});
