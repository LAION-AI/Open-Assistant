import { useColorMode } from "@chakra-ui/react";
import Image from "next/image";
import Link from "next/link";

export function Footer() {
  const { colorMode } = useColorMode();
  const bgColorClass = colorMode === "light" ? "bg-transparent" : "bg-gray-800";
  const borderClass = colorMode === "light" ? "border-slate-200" : "border-transparent";

  return (
    <footer className={bgColorClass}>
      <div className={`flex mx-auto max-w-7xl justify-between py-10 px-10 border-t ${borderClass}`}>
        <div className="flex items-center pr-8">
          <Link href="/" aria-label="Home" className="flex items-center">
            <Image src="/images/logos/logo.svg" className="mx-auto object-fill" width="52" height="52" alt="logo" />
          </Link>

          <div className="ml-2">
            <p className="text-base font-bold">Open Assistant</p>
            <p className="text-sm">Conversational AI for everyone.</p>
          </div>
        </div>

        <nav className="flex justify-center gap-20">
          <nav className="flex justify-center gap-20">
            <div className="flex flex-col text-sm leading-7">
              <b>Legal</b>
              <div className="flex flex-col leading-5">
                <Link href="/privacy-policy" aria-label="Privacy Policy" className="hover:underline underline-offset-2">
                  Privacy Policy
                </Link>
                <Link
                  href="/terms-of-service"
                  aria-label="Terms of Service"
                  className="hover:underline underline-offset-2"
                >
                  Terms of Service
                </Link>
              </div>
            </div>
            <div className="flex flex-col text-sm leading-7">
              <b>Connect</b>
              <div className="flex flex-col leading-5">
                <Link
                  href="https://github.com/LAION-AI/Open-Assistant"
                  rel="noopener noreferrer nofollow"
                  target="_blank"
                  aria-label="Privacy Policy"
                  className="hover:underline underline-offset-2"
                >
                  Github
                </Link>
                <Link
                  href="https://discord.gg/pXtnYk9c"
                  rel="noopener noreferrer nofollow"
                  target="_blank"
                  aria-label="Terms of Service"
                  className="hover:underline underline-offset-2"
                >
                  Discord
                </Link>
              </div>
            </div>
          </nav>
          {/* </div> */}
        </nav>
      </div>
    </footer>
  );
}
