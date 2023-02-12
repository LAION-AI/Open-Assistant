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

  /**
   * time the user was created
   */
  created_date: string; // iso date string

  /**
   * if the user is shown on leaderboards
   */
  show_on_leaderboard: boolean;

  /**
   * streak
   */
  streak_days: unknown;

  /**
   * last day of latest streak
   */
  streak_last_day_date: string | null; // iso date string

  /**
   * last time this use made an interaction with the backend
   */
  last_activity_date: string | null; // iso date string

  /**
   * the date when the user accepted terms of the service
   */
  tos_acceptance_date: string | null; // iso date string
}

/**
 * An expanded User for the web.
 */
export interface User<TRole extends string = string> extends BackendUser {
  /**
   * The user's roles within the webapp.
   */
  role: TRole;
}

export type FetchUsersParams = {
  limit: number;
  cursor?: string;
  direction: "forward" | "back";
  searchDisplayName?: string;
  sortKey?: "username" | "display_name";
};

export type FetchUsersResponse<T extends User | BackendUser = BackendUser> = {
  items: T[];
  next?: string;
  prev?: string;
  sort_key: "username" | "display_name";
  order: "asc" | "desc";
};
