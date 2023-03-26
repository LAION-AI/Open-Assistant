-- CreateTable
CREATE TABLE "InferenceCredentials" (
    "userId" TEXT NOT NULL,
    "provider" TEXT,
    "providerAccountId" TEXT,
    "accessToken" TEXT,
    "accessTokenType" TEXT,
    "refreshToken" TEXT,
    "refreshTokenType" TEXT,
    "expiresAt" INTEGER,

    CONSTRAINT "InferenceCredentials_pkey" PRIMARY KEY ("userId")
);

-- AddForeignKey
ALTER TABLE "InferenceCredentials" ADD CONSTRAINT "InferenceCredentials_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
