export interface BackendUserCore {
  /**
   * The user's unique ID according to the `auth_method`.
   */
  id: string;

  /**
   * The user's set name
   */
  display_name: string;

  /**
   * The authorization method.  One of:
   *   - discord
   *   - local
   */
  auth_method: string;
}

/**
 * Reports the Backend's knowledge of a user.
 */
export interface BackendUser extends BackendUserCore {
  /**
   * The backend's UUID for this user.
   */
  user_id: string;

  /**
   * Arbitrary notes about the user.
   */
  notes: string;

  /**
   * True when the user is able to access the platform.  False otherwise.
   */
  enabled: boolean;

  /**
   * True when the user is marked for deletion.  False otherwise.
   */
  deleted: boolean;
}

/**
 * An expanded User for the web.
 */
export interface User extends BackendUser {
  /**
   * The user's roles within the webapp.
   */
  role: string;
}
