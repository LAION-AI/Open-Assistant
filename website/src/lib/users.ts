import { Account } from "@prisma/client";
import prisma from "src/lib/prismadb";
import type { BackendUserCore } from "src/types/Users";

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
 * convert a user object to a canoncial representation used for interacting with the backend
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
    auth_method: user.accounts[0].provider,
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
export const getFrontendUserIdForDiscordUser = async (id: string) => {
  const { userId } = await prisma.account.findFirst({ where: { provider: "discord", providerAccountId: id } });
  return userId;
};

/**
 *
 * @param {string} username the id of the user, this field is called 'username' in the python backend's user table
 * not to be confused with the user's UUID
 * @param auth_method either "local" or "discord"
 */
export const getFrontendUserIdFromBackendUser = async (username: string, auth_method: string) => {
  if (auth_method === "local") {
    return username;
  } else if (auth_method === "discord") {
    return getFrontendUserIdForDiscordUser(username);
  }
  throw new Error(`Unexpected auth_method: ${auth_method}`);
};

/**
 * this function is similar to `getFrontendUserIdFromBackendUser`, but optimized for reducing the
 * number of database calls if fetching the data for many users (i.e. leaderboard)
 */
export const getBatchFrontendUserIdFromBackendUser = async (users: { username: string; auth_method: string }[]) => {
  // for users signed up with email, the 'username' field from the backend is the id of the user in the frontend db
  // we initialize the output for all users with the username for now:
  const outputIds = users.map((user) => user.username);

  // handle discord users a bit differently
  const indicesOfDiscordUsers = users
    .map((user, idx) => ({ idx, isDiscord: user.auth_method === "discord" }))
    .filter((x) => x.isDiscord)
    .map((x) => x.idx);

  if (indicesOfDiscordUsers.length === 0) {
    // no discord users, save a database call
    return outputIds;
  }

  // get the frontendUserIds for the discord users
  // the `username` field for discord users is the id of the discord account
  const discordAccountIds = indicesOfDiscordUsers.map((idx) => users[idx].username);
  const discordAccounts = await prisma.account.findMany({
    where: {
      provider: "discord",
      providerAccountId: { in: discordAccountIds },
    },
    select: { userId: true, providerAccountId: true },
  });

  indicesOfDiscordUsers.forEach((userIdx) => {
    // NOTE: findMany will return the values unsorted, which is why we have to 'find' here
    const account = discordAccounts.find((a) => a.providerAccountId === users[userIdx].username);
    outputIds[userIdx] = account.userId;
  });

  return outputIds;
};
