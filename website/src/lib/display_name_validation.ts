export const validDisplayNameRegex = /^\S+/g;
/**
 * Given a user's display name and its ID, returns a valid display name,
 * checking if the original display name is invalid (e.g. empty or starts
 * with whitespace).
 *
 * @param {string} displayName The user's display name.
 * @param {string} id The user's ID.
 * @returns {string} A valid display name.
 */
export const getValidDisplayName = (displayName: string, id: string): string => {
  return !isValidDisplayName(displayName) ? id : displayName;
};

export const isValidDisplayName = (displayName: string) => {
  return displayName && displayName.match(validDisplayNameRegex);
};
