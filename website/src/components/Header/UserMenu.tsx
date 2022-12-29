import React from "react";
import { signOut, useSession } from "next-auth/react";
import Image from "next/image";
import { Popover } from "@headlessui/react";
import { AnimatePresence, motion } from "framer-motion";
import { FaCog, FaSignOutAlt, FaGithub } from "react-icons/fa";
import { Box, useColorModeValue } from "@chakra-ui/react";

export function UserMenu() {
  const { data: session } = useSession();
  const backgroundColor = useColorModeValue("#FFFFFF", "#000000");

  if (!session) {
    return <></>;
  }
  if (session && session.user) {
    const email = session.user.email;
    const accountOptions = [
      {
        name: "Account Settings",
        href: "/account",
        desc: "Account Settings",
        icon: FaCog,
        //For future use
      },
    ];
    return (
      <Popover className="relative">
        {({ open }) => (
          <>
            <Popover.Button aria-label="Toggle Account Options" className="flex">
              <div className="flex items-center gap-4 p-1 lg:pr-6 rounded-full border border-slate-300/70 hover:bg-gray-200/50 transition-colors duration-300">
                <Image
                  src="/images/temp-avatars/av1.jpg"
                  alt="Profile Picture"
                  width="40"
                  height="40"
                  className="rounded-full"
                ></Image>
                <p className="hidden lg:flex">{session.user.name || session.user.email}</p>
              </div>
            </Popover.Button>
            <AnimatePresence initial={false}>
              {open && (
                <Box backgroundColor={backgroundColor}>
                  <Popover.Panel
                    static
                    as={motion.div}
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{
                      opacity: 0,
                      y: -10,
                      transition: { duration: 0.2 },
                    }}
                    className="absolute right-0 mt-3 w-screen bg-inherit max-w-xs p-4 rounded-md border border-slate-300/70"
                  >
                    <Box className="flex flex-col gap-1">
                      {accountOptions.map((item) => (
                        <a
                          key={item.name}
                          href={item.href}
                          aria-label={item.desc}
                          className="flex items-center rounded-md hover:bg-gray-200/50"
                        >
                          <div className="p-4">
                            <item.icon aria-hidden="true" />
                          </div>
                          <div>
                            <p>{item.name}</p>
                          </div>
                        </a>
                      ))}
                      <a
                        className="flex items-center rounded-md hover:bg-gray-100 cursor-pointer"
                        onClick={() => signOut({ callbackUrl: "/" })}
                      >
                        <div className="p-4">
                          <FaSignOutAlt />
                        </div>
                        <div>
                          <p>Sign Out</p>
                        </div>
                      </a>
                    </Box>
                  </Popover.Panel>
                </Box>
              )}
            </AnimatePresence>
          </>
        )}
      </Popover>
    );
  }
}

export default UserMenu;
