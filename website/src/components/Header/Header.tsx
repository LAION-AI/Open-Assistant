import { Box, Button } from "@chakra-ui/react";
import { Popover } from "@headlessui/react";
import { AnimatePresence, motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { FaUser } from "react-icons/fa";
import { UserMenu } from "./UserMenu";

function MenuIcon(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" {...props}>
      <path d="M5 6h14M5 18h14M5 12h14" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function ChevronUpIcon(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" {...props}>
      <path d="M17 14l-5-5-5 5" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function MobileNavLink({ children, ...props }) {
  return (
    <Popover.Button
      as={Link}
      href={props.href}
      className="block text-base leading-7 tracking-tight text-gray-700"
      {...props}
    >
      {children}
    </Popover.Button>
  );
}

function AccountButton() {
  const { data: session } = useSession();
  if (session) {
    return;
  }
  return (
    <Link href="/auth/signin" aria-label="Home" className="flex items-center">
      <Button variant="outline" leftIcon={<FaUser />}>
        Sign in
      </Button>
    </Link>
  );
}

export function Header(props) {
  return (
    <header>
      <nav>
        <Box className="relative z-10 flex justify-between px-4 py-4">
          <div className="relative z-10 flex items-center gap-10">
            <Link href="/" aria-label="Home" className="flex items-center">
              <Image src="/images/logos/logo.svg" className="mx-auto object-fill" width="50" height="50" alt="logo" />
              <span className="text-2xl font-bold ml-3">Open Assistant</span>
            </Link>
          </div>
          <div className="flex items-center gap-4">
            <Popover className="lg:hidden">
              {({ open }) => (
                <>
                  <Popover.Button
                    className="relative z-10 inline-flex items-center rounded-lg stroke-slate-600 p-2 hover:bg-slate-100 hover:stroke-slate-900 active:stroke-gray-900 [&:not(:focus-visible)]:focus:outline-none transition-colors duration-300"
                    aria-label="Toggle site navigation"
                  >
                    {({ open }) => (open ? <ChevronUpIcon className="h-6 w-6" /> : <MenuIcon className="h-6 w-6" />)}
                  </Popover.Button>
                  <AnimatePresence initial={false}>
                    {open && (
                      <>
                        <Popover.Overlay
                          static
                          as={motion.div}
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          exit={{ opacity: 0 }}
                          className="fixed inset-0 z-1 bg-slate-200/60 backdrop-blur"
                        />
                        <Popover.Panel
                          static
                          as={motion.div}
                          initial={{ opacity: 0, y: -32 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{
                            opacity: 0,
                            y: -32,
                            transition: { duration: 0.2 },
                          }}
                          className="w-full absolute inset-x-0 top-0 z-0 origin-top rounded-b-lg bg-white px-6 pb-10 pt-32 shadow-sm shadow-slate-200"
                        >
                          <div className="space-y-4">
                            <MobileNavLink href="/#join-us">Join Us</MobileNavLink>
                            <MobileNavLink href="/#faqs">FAQs</MobileNavLink>
                          </div>
                          <div className="mt-8 flex flex-col gap-4"></div>
                        </Popover.Panel>
                      </>
                    )}
                  </AnimatePresence>
                </>
              )}
            </Popover>
            <AccountButton />
            <UserMenu />
          </div>
        </Box>
      </nav>
    </header>
  );
}
