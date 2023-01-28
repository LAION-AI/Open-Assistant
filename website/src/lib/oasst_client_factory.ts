import { JWT } from "next-auth/jwt";
import { OasstApiClient } from "src/lib/oasst_api_client";
import { getBackendUserCore } from "src/lib/users";
import { BackendUserCore } from "src/types/Users";

export const createApiClientFromUser = (user: BackendUserCore) =>
  new OasstApiClient(process.env.FASTAPI_URL, process.env.FASTAPI_KEY, user);

export const createApiClient = async (token: JWT) => createApiClientFromUser(await getBackendUserCore(token.sub));

export const userlessApiClient = new OasstApiClient(process.env.FASTAPI_URL, process.env.FASTAPI_KEY);
