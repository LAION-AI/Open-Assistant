import axios from "axios";
import { secondsInHour } from "date-fns";
import { withoutRole } from "src/lib/auth";
import prisma from "src/lib/prismadb";
import { nowUnix } from "src/lib/time";
import { InferenceTokens } from "src/types/Chat";

export default withoutRole("banned", async (req, res, token) => {
  const { code, parts } = req.query;

  if (!Array.isArray(parts) || parts.length !== 1) {
    return res.status(400).end();
  }

  const [provider] = parts as string[];
  const url = process.env.INFERENCE_SERVER_HOST + `/auth/callback/${provider}?code=${code}`;
  const { data } = await axios<InferenceTokens>(url);

  const inferenceDbData = {
    userId: token.sub,
    provider,
    accessToken: data.access_token.access_token,
    accessTokenType: data.access_token.token_type,
    refreshToken: data.refresh_token.access_token,
    refreshTokenType: data.refresh_token.token_type,
    // TODO: we should update our inference backend to give us this information
    expiresAt: nowUnix() + secondsInHour,
  };
  await prisma.inferenceCredentials.upsert({
    where: { userId: token.sub },
    update: inferenceDbData,
    create: inferenceDbData,
  });
  // TODO: redirect to original page the user was on, use the state query parameter
  return res.redirect(`/chat`);
});
