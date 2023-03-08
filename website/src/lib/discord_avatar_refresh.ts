import { Account } from "@prisma/client";

import prisma from "./prismadb";

const ONE_DAY_IN_MILLISECONDS = 1000 * 60 * 60 * 24;

class DiscordAvatarRefresher {
  private readonly lastUpdated: Record<string, number> = {};

  async updateImageIfNecessary(account?: Account) {
    if (!account) {
      return;
    }

    const { access_token, token_type, providerAccountId, provider, userId } = account;
    console.assert(provider === "discord");

    const lastUpdate = this.lastUpdated[providerAccountId];
    const now = Date.now();
    if (lastUpdate && now - lastUpdate < ONE_DAY_IN_MILLISECONDS) {
      // updated recently, ignore
      return;
    }

    this.lastUpdated[providerAccountId] = now;
    try {
      const user = await fetch("https://discord.com/api/v10/users/@me", {
        headers: { Authorization: `${token_type} ${access_token}` },
      }).then((res) => res.json());

      const imgURL = `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png`;
      await prisma.user.update({
        where: { id: userId },
        data: { image: imgURL },
      });
    } catch (err) {
      console.error(err);
      // mark as refresh-able
      delete this.lastUpdated[providerAccountId];
    }
  }
}

const globalForRefresh = global as unknown as { discordAvatarRefresh: DiscordAvatarRefresher };

export const discordAvatarRefresh = globalForRefresh.discordAvatarRefresh || new DiscordAvatarRefresher();
