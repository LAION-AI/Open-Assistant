import { getValidDisplayName } from "src/lib/display_name_validation";
import prisma from "src/lib/prismadb";
import { getBatchFrontendUserIdFromBackendUser } from "src/lib/users";
import { AuthMethod } from "src/types/Providers";

export const updateUsersDisplayNames = <T extends { display_name: string; username: string }>(entries: T[]) => {
  return entries.map((entry) => ({
    ...entry,
    display_name: getValidDisplayName(entry.display_name, entry.username),
  }));
};

export const updateUsersProfilePictures = async <T extends { auth_method: AuthMethod; username: string }>(
  entries: T[]
) => {
  const frontendUserIds = await getBatchFrontendUserIdFromBackendUser(entries);

  const items = await prisma.user.findMany({
    where: { id: { in: frontendUserIds } },
    select: { image: true, id: true },
  });

  return entries.map((entry, idx) => ({
    ...entry,
    // NOTE: findMany will return the values unsorted, which is why we have to 'find' here
    // TODO: Check why there is no image for a better fix
    image: items.find((i) => i.id === frontendUserIds[idx])?.image || "",
  }));
};
