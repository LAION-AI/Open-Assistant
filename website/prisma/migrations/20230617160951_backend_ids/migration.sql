-- CreateTable
CREATE TABLE "BackendInfo" (
    "id" TEXT NOT NULL,
    "frontendUserId" TEXT NOT NULL,
    "backendUserId" TEXT NOT NULL,

    CONSTRAINT "BackendInfo_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "BackendInfo_frontendUserId_key" ON "BackendInfo"("frontendUserId");

-- CreateIndex
CREATE UNIQUE INDEX "BackendInfo_backendUserId_key" ON "BackendInfo"("backendUserId");

-- AddForeignKey
ALTER TABLE "BackendInfo" ADD CONSTRAINT "BackendInfo_frontendUserId_fkey" FOREIGN KEY ("frontendUserId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
