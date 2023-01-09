/**
 * A seed function to inject test data into the web database.
 *
 * Use by running
 *   npx prisma db seed
 */

import { PrismaClient } from "@prisma/client";
const prisma = new PrismaClient();

async function main() {
  const users = [
    { email: "general.user.a@example.com", name: "A", role: "general" },
    { email: "general.user.b@example.com", name: "B", role: "general" },
    { email: "general.user.c@example.com", name: "C", role: "general" },
    { email: "general.user.d@example.com", name: "D", role: "general" },
    { email: "general.user.e@example.com", name: "E", role: "general" },
    { email: "general.user.f@example.com", name: "F", role: "general" },
    { email: "general.user.g@example.com", name: "G", role: "general" },
    { email: "general.user.h@example.com", name: "H", role: "general" },
    { email: "general.user.i@example.com", name: "I", role: "general" },
    { email: "general.user.j@example.com", name: "J", role: "general" },
    { email: "general.user.k@example.com", name: "K", role: "general" },
    { email: "general.user.l@example.com", name: "L", role: "general" },
    { email: "general.user.m@example.com", name: "M", role: "general" },
    { email: "general.user.n@example.com", name: "N", role: "general" },
    { email: "general.user.o@example.com", name: "O", role: "general" },
    { email: "general.user.p@example.com", name: "P", role: "general" },
    { email: "general.user.q@example.com", name: "Q", role: "general" },
    { email: "general.user.r@example.com", name: "R", role: "general" },
    { email: "malicious.user.1@example.com", name: "M1", role: "general" },
    { email: "malicious.user.2@example.com", name: "M2", role: "general" },
  ];
  await Promise.all(
    users.map(async ({ email, name, role }) => {
      await prisma.user.upsert({
        where: { email },
        update: { name, role },
        create: {
          email,
          name,
          role,
        },
      });
    })
  );
}

main()
  .then(async () => {
    await prisma.$disconnect();
  })
  .catch(async (e) => {
    console.error(e);
    await prisma.$disconnect();
    process.exit(1);
  });
