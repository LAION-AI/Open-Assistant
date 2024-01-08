import { Account } from "@prisma/client";
import prisma from "src/lib/prismadb";
import { AuthMethod } from "src/types/Providers";
import type { BackendUserCore } from "src/types/Users";

import { logger } from "./logger";
import { OasstError } from "./oasst_api_client";
import { userlessApiClient } from "./oasst_client_factory";

/**
 * Returns a `BackendUserCore` that can be used for interacting with the Backend service.
 *
 * @param {string} id The user's web auth id.
 *
 */
export const getBackendUserCore = async (id: string): Promise<BackendUserCore> => {
  const user = await prisma.user.findUnique({
    where: { id },
    select: { id: true, name: true, accounts: true },
  });
  if (!user) {
    throw new Error("User not found");
  }
  return convertToBackendUserCore(user);
};

/**
 * convert a user object to a canonical representation used for interacting with the backend
 * @param user frontend user object, from prisma db
 */
export const convertToBackendUserCore = <T extends { accounts: Account[]; id: string; name: string }>(
  user: T
): BackendUserCore => {
  // If there are no linked accounts, just use what we have locally.
  if (user.accounts.length === 0) {
    return {
      id: user.id,
      display_name: user.name,
      auth_method: "local",
    };
  }

  // Otherwise, use the first linked account that the user created.
  return {
    id: user.accounts[0].providerAccountId,
    display_name: user.name,
    auth_method: user.accounts[0].provider as AuthMethod,
  };
};

/**
 * The frontend user id for discord users is saved differently from the email users
 *
 * this functions gets the "correct" user id for interacting with the frontend db, more specifically
 * the users table, when calling `prisma.user....`
 *
 * Ideally, this function does not need to exist, but this might require huge migrations
 *
 * @param {string} id the id of the user, this field is called 'username' in the python backend's user table
 * not to be confused with the user's UUID
 */
export const getFrontendUserIdForUser = async (id: string, provider: Exclude<AuthMethod, "local">) => {
  const { userId } = await prisma.account.findFirst({ where: { provider: provider, providerAccountId: id } });
  return userId;
};

/**
 * Map backend users to their frontend ids, we might have to do a db call to
 */
export const getBatchFrontendUserIdFromBackendUser = async (users: { username: string; auth_method: AuthMethod }[]) => {
  // for users signed up with email, the 'username' field from the backend is the id of the user in the frontend db
  // we initialize the output for all users with the username for now:
  const outputIds = users.map((user) => user.username);

  // handle non-local users differently
  const indicesOfNonLocalUsers = users
    .map((user, idx) => ({ idx, isNonLocal: user.auth_method !== "local" }))
    .filter((x) => x.isNonLocal)
    .map((x) => x.idx);

  if (indicesOfNonLocalUsers.length === 0) {
    // no external users, save a database call
    return outputIds;
  }

  // get the frontendUserIds for the external users
  // the `username` field for external users is the id of the their account at the provider
  const externalAccountIds = indicesOfNonLocalUsers.map((idx) => users[idx].username);
  const externalAccounts = await prisma.account.findMany({
    where: {
      provider: { in: ["discord", "google"] },
      providerAccountId: { in: externalAccountIds },
    },
    select: { userId: true, providerAccountId: true, provider: true },
  });

  indicesOfNonLocalUsers.forEach((userIdx) => {
    // NOTE: findMany will return the values unsorted, which is why we have to 'find' here
    const account = externalAccounts.find(
      (a) => a.provider === users[userIdx].auth_method && a.providerAccountId === users[userIdx].username
    );

    if (account) {
      outputIds[userIdx] = account.userId;
    } else {
      logger.warn(`[getBatchFrontendUserIdFromBackendUser] account is undefined`, {
        users_length: users.length,
        userIdx,
        user: users[userIdx],
      });
    }
  });

  return outputIds;
};

/**
 * merges all backend users into one, and saves the value in the database
 *
 * This function is currently unused
 *
 * TODO: do we need to make this idempotent? should we check if the user is already merged
 * before we continue with the merging?
 */
export const mergeUserAccountsInBackend = async (frontendId: string): Promise<string | null> => {
  const user = await prisma.user.findUnique({
    where: { id: frontendId },
    select: { id: true, name: true, emailVerified: true, accounts: true },
  });

  const accounts = user.accounts
    .map((x) => ({
      auth_method: x.provider as AuthMethod,
      id: x.providerAccountId,
    }))
    .concat([{ auth_method: "local", id: frontendId }]);

  const backendUsers = await Promise.all(
    accounts.map((account) =>
      userlessApiClient.fetch_frontend_user(account).catch<null>((err) => {
        // if 404, thats okay
        if (!(err instanceof OasstError) || err.httpStatusCode !== 404) {
          console.error(err);
        }
        return null;
      })
    )
  );

  const backendIds = backendUsers.filter(Boolean).map((user) => user.user_id);
  if (backendIds.length === 0) {
    logger.error({ message: `Wanted to merge user accounts but found none.`, frontendId, accounts });
    return null;
  }

  // id after merge
  let backendId: string;

  if (backendIds.length === 1) {
    backendId = backendIds[0];
    logger.info({ message: `Wanted to merge user accounts, but found only one, skipping.`, frontendId, backendId });
  } else {
    logger.info({ message: "Merging user accounts", frontendId, accounts, backendIds });
    let remainingIds: string[];

    [backendId, ...remainingIds] = backendIds;

    await userlessApiClient.merge_backend_users(backendId, remainingIds);
    logger.info({ message: "Merging successful", frontendId, accounts, backendIds });
  }

  // write to database
  await prisma.backendInfo.upsert({
    where: {
      frontendUserId: frontendId,
    },
    create: {
      frontendUserId: frontendId,
      backendUserId: backendId,
    },
    update: {
      backendUserId: backendId,
    },
  });

  return backendId;
};
