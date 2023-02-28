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
    select: {
      id: true,
      name: true,
      accounts: true,
    },
  });

  if (!user) {
    throw new Error("User not found");
  }

  // If there are no linked accounts, just use what we have locally.
  if (user.accounts.length === 0) {
    return {
      id: user.id,
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      display_name: user.name!,
      auth_method: "local",
    };
  }

  // Otherwise, use the first linked account that the user created.
  return {
    id: user.accounts[0].providerAccountId,
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    display_name: user.name!,
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
