export type ExternalProvider = "google" | "discord";

export interface UserAccountResponse {
  emailIsVerified: boolean;
  accounts: Array<{ provider: ExternalProvider; providerAccountId: string }>;
}
