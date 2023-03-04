import { getValidDisplayName } from "src/lib/display_name_validation";
import { getBatchFrontendUserIdFromBackendUser } from "src/lib/users";

export const updateUsersDisplayNames = <T extends { display_name: string; username: string }>(entries: T[]) => {
  return entries.map((entry) => ({
    ...entry,
    display_name: getValidDisplayName(entry.display_name, entry.username),
  }));
};

export const updateUsersProfilePictures = async <T extends { auth_method: string; username: string }>(entires: T[]) => {
  const frontendUserIds = await getBatchFrontendUserIdFromBackendUser(entires);

  const items = await prisma.user.findMany({
    where: { id: { in: frontendUserIds } },
    select: { image: true },
  });

  return entires.map((entry, idx) => ({ ...entry, image: items[idx].image }));
};
